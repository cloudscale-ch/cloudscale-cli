"""Commands shared by all cloudscale.ch API resources."""

import sys
import time
from collections.abc import Iterable
from typing import Any, NoReturn

import click
import jmespath
from cloudscale import Cloudscale, CloudscaleApiException
from natsort import natsorted, ns

from .output import to_pretty_json, to_table, transform_json
from .spinner import Spinner
from .tags import merge_tags, tags_to_dict


def abort(message: object) -> NoReturn:
    """Write an error message to stderr and exit with a failure."""
    click.echo(message, err=True)
    sys.exit(1)


def uuid_of(resource: dict, default: str = "") -> str:
    """Return the identifier of a resource, taken from its API href."""
    href = resource.get("href")
    return href.rsplit("/", maxsplit=1)[-1] if href else default


class CloudscaleCommand:
    """Implements the commands available for every API resource.

    One instance is created per CLI invocation and handed to the command
    group of the resource in use, which then configures it by setting the
    attributes below.
    """

    def __init__(
        self,
        cloud_resource_name: str | None = None,
        api_token: str | None = None,
        profile: str | None = None,
        debug: bool = False,
        output: str = "table",
        verbose: bool = False,
    ):
        self._credentials = {
            "api_token": api_token,
            "profile": profile,
            "debug": debug,
        }
        self._client: Cloudscale | None = None
        self._output = output

        #: Name of the resource as known by the SDK, e.g. "server_group".
        self.cloud_resource_name = cloud_resource_name
        self.verbose = verbose
        #: Fields shown in table output, in order.
        self.headers: list[str] = []
        #: Field holding the name, resources without a name set it to None.
        self.resource_name_key: str | None = "name"
        #: Name of the identifier, some resources do not use a UUID.
        self.resource_uuid_name: str = "UUID"
        #: Field to sort the table by, defaults to the name field.
        self.resource_table_sort_key: str | None = None
        #: JMESPath expression flattening the API response for table output.
        self.response_transform_json: str | None = None

    @property
    def client(self) -> Cloudscale:
        """The API client, created on first use.

        Creating it requires an API token, so it is deferred to keep
        ``--help`` working without any credentials configured.
        """
        if self._client is None:
            try:
                self._client = Cloudscale(**self._credentials)
            except Exception as e:
                abort(e)
        return self._client

    @property
    def resource(self) -> Any:
        """The SDK client of the resource in use, e.g. ``Cloudscale().server``."""
        return getattr(self.client, self.cloud_resource_name)

    #
    # Output
    #

    def format_output(self, response: dict | list) -> str:
        """Render an API response in the output format requested."""
        if self._output == "json":
            return to_pretty_json(response)

        rows = [response] if isinstance(response, dict) else response
        if rows:
            rows = self._sorted(transform_json(rows, self.response_transform_json))
        return to_table(rows, self.headers)

    def _sorted(self, rows: list[dict]) -> list[dict]:
        """Sort rows naturally by name, grouped by zone where available."""
        sort_key = self.resource_table_sort_key or self.resource_name_key
        if not sort_key:
            return rows

        def key(row: dict) -> Any:
            if "zone" in self.headers:
                return (row["zone"], row[sort_key])
            return row[sort_key]

        return natsorted(rows, key=key, alg=ns.IGNORECASE)

    #
    # Lookups
    #

    def find_by_name(self, name: str) -> list[dict]:
        """Return all resources matching a name."""
        if not self.resource_name_key:
            return []

        with Spinner(text=f"Querying by {self.resource_name_key} {name}"):
            return [
                resource
                for resource in self.resource.get_all()
                if resource.get(self.resource_name_key) == name
            ]

    def find(self, identifier: str) -> tuple[str, list[dict]]:
        """Look up a resource by identifier, falling back to its name.

        Returns the identifier of the resource, resolved if a name was
        given, together with all resources matching. Exits if none matched.
        """
        try:
            with Spinner(text=f"Querying by {self.resource_uuid_name} {identifier}"):
                return identifier, [self.resource.get_by_uuid(uuid=identifier)]
        except CloudscaleApiException:
            pass

        results = self.find_by_name(name=identifier)
        if not results:
            self._abort_not_found(identifier)

        if len(results) == 1:
            identifier = uuid_of(results[0], default=identifier)
        return identifier, results

    def find_one(self, identifier: str) -> tuple[str, dict]:
        """Look up a single resource, exiting if the name is ambiguous."""
        identifier, results = self.find(identifier)
        if len(results) > 1:
            abort(
                f"Error: More than one resource found for {self.cloud_resource_name} "
                f"having name: {identifier}. Please use {self.resource_uuid_name} "
                "to select the resource."
            )
        return identifier, results[0]

    def _abort_not_found(self, identifier: str) -> NoReturn:
        keys = self.resource_uuid_name
        if self.resource_name_key:
            keys = f"{keys} or {self.resource_name_key}"
        abort(
            f"No resource found for {self.cloud_resource_name} "
            f"having {keys}: {identifier}"
        )

    #
    # Commands
    #

    def cmd_list(
        self,
        filter_tag: str | None = None,
        filter_json: str | None = None,
        action: str | None = None,
        delete: bool = False,
        force: bool = False,
        wait: bool = False,
    ) -> None:
        """List resources, optionally acting on all of them."""
        if action and delete:
            abort("Error: --action and --delete are mutually exclusive")

        try:
            with Spinner(text="Querying"):
                response = self.resource.get_all(filter_tag=filter_tag)

            if filter_json:
                try:
                    response = jmespath.search(filter_json, response)
                except Exception as e:
                    abort(f"filter_json error: {e}")

            if not response:
                return

            click.echo(self.format_output(response))

            if delete:
                self._delete_all(response, force=force)
            elif action:
                self._act_on_all(
                    response,
                    action=action,
                    force=force,
                    wait=wait,
                    filter_tag=filter_tag,
                )
        except Exception as e:
            abort(e)

    def _delete_all(self, resources: list[dict], force: bool) -> None:
        if not force:
            click.confirm("Do you want to delete?", abort=True)

        for uuid in self._uuids_of(resources, "delete"):
            self.cmd_delete(uuid=uuid, force=True, skip_query=True)

    def _act_on_all(
        self,
        resources: list[dict],
        action: str,
        force: bool,
        wait: bool,
        filter_tag: str | None,
    ) -> None:
        if not force:
            click.confirm(f"Do you want to {action}?", abort=True)

        for uuid in self._uuids_of(resources, action):
            with Spinner(text=f"{action.capitalize()} {uuid}"):
                getattr(self.resource, action)(uuid)

        if wait:
            for resource in self.resource.get_all(filter_tag=filter_tag):
                self.wait_for_status(uuid=uuid_of(resource))

        with Spinner(text="Querying"):
            response = self.resource.get_all(filter_tag=filter_tag)
        click.echo(self.format_output(response))

    def _uuids_of(self, resources: list[dict], action: str) -> list[str]:
        """Return the identifiers of resources, exiting if one is unknown."""
        uuids = []
        for resource in resources:
            if "href" not in resource:
                abort(f"No href found, could not {action}.")
            uuids.append(uuid_of(resource))
        return uuids

    def cmd_show(self, uuid: str) -> None:
        """Show a single resource, looked up by identifier or name."""
        try:
            _, results = self.find(uuid)
        except Exception as e:
            abort(e)

        click.echo(self.format_output(results[0] if len(results) == 1 else results))

    def cmd_create(self, silent: bool = False, **kwargs: Any) -> dict | None:
        """Create a resource."""
        try:
            if "tags" in kwargs:
                kwargs["tags"] = self.parse_tags(kwargs["tags"])

            name = kwargs.get(self.resource_name_key, "")
            with Spinner(text=f"Creating {name}"):
                response = self.resource.create(**kwargs)
        except Exception as e:
            abort(e)

        if silent:
            return response

        click.echo(self.format_output(response))
        return response

    def cmd_update(
        self,
        uuid: str,
        tags: Iterable[str] = (),
        clear_tags: Iterable[str] = (),
        clear_all_tags: bool = False,
        wait: bool = False,
        **kwargs: Any,
    ) -> None:
        """Update a resource, looked up by identifier or name."""
        try:
            uuid, _ = self.find_one(uuid)

            with Spinner(text="Processing tags"):
                new_tags = self._updated_tags(uuid, tags, clear_tags, clear_all_tags)

            with Spinner(text=f"Updating by {self.resource_uuid_name} {uuid}"):
                self.resource.update(uuid=uuid, tags=new_tags, **kwargs)

            if wait:
                response = self.wait_for_status(uuid=uuid)
            else:
                with Spinner(text=f"Querying {uuid}"):
                    response = self.resource.get_by_uuid(uuid=uuid)

            click.echo(self.format_output(response))
        except Exception as e:
            abort(e)

    def _updated_tags(
        self,
        uuid: str,
        tags: Iterable[str],
        clear_tags: Iterable[str],
        clear_all_tags: bool,
    ) -> dict[str, str] | None:
        """Return the tags to send to the API, or None to keep them as is."""
        if not any([tags, clear_tags, clear_all_tags]):
            return None

        current = {}
        if not clear_all_tags:
            current = self.resource.get_by_uuid(uuid=uuid).get("tags") or {}

        try:
            return merge_tags(current, add=tags, clear=clear_tags)
        except ValueError as e:
            abort(e)

    def cmd_delete(self, uuid: str, force: bool = False, skip_query: bool = False):
        """Delete a resource, looked up by identifier or name."""
        try:
            if not skip_query:
                uuid, resource = self.find_one(uuid)
                click.echo(self.format_output(resource))

            if not force:
                click.confirm("Do you want to delete?", abort=True)

            with Spinner(text=f"Deleting by {self.resource_uuid_name} {uuid}"):
                self.resource.delete(uuid)

            click.echo(f"{uuid} deleted!")
        except Exception as e:
            abort(e)

    def cmd_act(self, action: str, uuid: str, wait: bool = False) -> None:
        """Run an action, e.g. "start", on a resource."""
        try:
            uuid, _ = self.find_one(uuid)

            with Spinner(text=f"{action} {uuid}"):
                getattr(self.resource, action)(uuid)

            if wait:
                response = self.wait_for_status(uuid=uuid)
            else:
                with Spinner(text=f"Querying {uuid}"):
                    response = self.resource.get_by_uuid(uuid=uuid)

            click.echo(self.format_output(response))
        except Exception as e:
            abort(e)

    def parse_tags(self, tags: Iterable[str]) -> dict[str, str] | None:
        """Turn tags given on the command line into a dict."""
        try:
            return tags_to_dict(tags)
        except ValueError as e:
            abort(e)

    def wait_for_status(
        self,
        uuid: str,
        status: str = "changing",
        max_sleep: int = 4,
        retries: int = 30,
        path: str = "",
    ) -> dict:
        """Query a resource until it left a transitional status."""
        response: dict = {}
        with Spinner(text=f"Waiting for status {uuid}: ...") as spinner:
            for retry in range(retries):
                response = self.resource.get_by_uuid(uuid=uuid, path=path)
                if response["status"] != status:
                    break

                spinner.text = (
                    f"Waiting for {uuid} to finish, "
                    f"current status: {response['status']} {retry * '.'}"
                )
                # Backoff exponentially, but not longer than max_sleep.
                time.sleep(min(2**retry, max_sleep))
            else:
                spinner.text = f"Waiting for status {uuid} timed out."
                time.sleep(1)
        return response
