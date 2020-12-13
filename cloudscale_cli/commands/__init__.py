import sys
import time
import click
import jmespath
from natsort import natsorted, ns
from cloudscale import Cloudscale, CloudscaleApiException
from ..util import to_table, to_pretty_json, tags_to_dict, format_json

if sys.stdout.isatty():
    from yaspin import yaspin as Spinner
else:
    from ..spinner import DummySpinner as Spinner

OUTPUT_FORMATS = [
    'table',
    'json',
]

class CloudscaleCommand:

    def __init__(self, cloud_resource_name=None, api_token=None, profile=None, debug=False, output="table", verbose=False):
        try:
            self._client = Cloudscale(
                api_token=api_token,
                profile=profile,
                debug=debug
            )
        except Exception as e:
            click.echo(e, err=True)
            sys.exit(1)

        self._output = output

        self.cloud_resource_name = cloud_resource_name
        self.verbose = verbose
        self.headers = []

        # Alternate key to look for the resource as 'name'
        self.resource_name_key = 'name'

        # Some resource have a different identifier name
        self.resource_uuid_name = 'UUID'

        # Usually we want to sort the table by the key used as name
        self.resource_table_sort_key = None

        self.response_transform_json = None

    def get_client_resource(self):
        return getattr(self._client, self.cloud_resource_name)

    def _handle_tags(self, tags):
        try:
            tags = tags_to_dict(tags)
            return tags
        except ValueError as e:
            click.echo(e, err=True)
            sys.exit(1)

    def _format_output(self, response):
        if self._output == "json":
            return to_pretty_json(response)
        else:
            if isinstance(response, dict):
                response = [response]

            if response:
                response = format_json(response, self.response_transform_json)
                sort_by_key = self.resource_table_sort_key or self.resource_name_key
                if sort_by_key:
                    if 'zone' in self.headers:
                        response = natsorted(response, key=lambda x: (x['zone'], x[sort_by_key]), alg=ns.IGNORECASE)
                    else:
                        response = natsorted(response, key=lambda x: x[sort_by_key], alg=ns.IGNORECASE)
            return to_table(response, self.headers)

    def cmd_list(self, filter_tag=None, filter_json=None, action=None, delete=False, force=False, wait=False):
        if action and delete:
            click.echo("Error: --action and --delete are mutually exclusive", err=True)
            sys.exit(1)
        try:
            with Spinner(text="Querying"):
                response = self.get_client_resource().get_all(filter_tag=filter_tag)
            if filter_json:
                try:
                    response = jmespath.search(filter_json, response)
                except Exception as e:
                    click.echo(f"filter_json error: {e}", err=True)
                    sys.exit(1)
            if response:
                click.echo(self._format_output(response))
                if delete:
                    if not force:
                        click.confirm(f"Do you want to delete?", abort=True)
                    for r in response:
                        if 'href' not in r:
                            click.echo("No href found, could not delete.", err=True)
                            sys.exit(1)
                        uuid = r['href'].split('/')[-1]
                        self.cmd_delete(uuid=uuid, force=True, skip_query=True)

                elif action:
                    if not force:
                        click.confirm(f"Do you want to {action}?", abort=True)
                    for r in response:
                        if 'href' not in r:
                            click.echo(f"No href found, could not {action}.", err=True)
                            sys.exit(1)
                        uuid = r['href'].split('/')[-1]
                        with Spinner(text=f"{action.capitalize()} {uuid}"):
                            getattr(self.get_client_resource(), action)(uuid)

                    if wait:
                        response = self.get_client_resource().get_all(filter_tag=filter_tag)
                        for r in response:
                            uuid = r['href'].split('/')[-1]
                            self.wait_for_status(uuid=uuid)

                    with Spinner(text="Querying"):
                        response = self.get_client_resource().get_all(filter_tag=filter_tag)
                    click.echo(self._format_output(response))
        except Exception as e:
            click.echo(e, err=True)
            sys.exit(1)

    def cmd_get_by_name(self, name):
        results = []
        if not self.resource_name_key:
            return results

        with Spinner(text=f"Querying by {self.resource_name_key} {name}"):
            responses = self.get_client_resource().get_all()
            for response in responses:
                if self.resource_name_key not in response:
                    break
                if response.get(self.resource_name_key) == name:
                    results.append(response)
        return results

    def cmd_show(self, uuid):
        try:
            with Spinner(text=f"Querying by {self.resource_uuid_name} {uuid}"):
                response = self.get_client_resource().get_by_uuid(uuid=uuid)
            click.echo(self._format_output(response))
        except CloudscaleApiException as e:
            results = self.cmd_get_by_name(name=uuid)
            if not results:
                if self.resource_name_key:
                    msg = f"No resource found for {self.cloud_resource_name} having {self.resource_uuid_name} or {self.resource_name_key}: {uuid}"
                else:
                    msg = f"No resource found for {self.cloud_resource_name} having {self.resource_uuid_name}: {uuid}"
                click.echo(msg, err=True)
                sys.exit(1)
            click.echo(self._format_output(results))
        except Exception as e:
            click.echo(e, err=True)
            sys.exit(1)

    def cmd_create(self, silent=False, **kwargs):
        try:
            if 'tags' in kwargs:
                kwargs['tags'] = self._handle_tags(kwargs['tags'])

            name = kwargs.get(self.resource_name_key, '')
            with Spinner(text=f"Creating {name}"):
                response = self.get_client_resource().create(**kwargs)
            if not silent:
                click.echo(self._format_output(response))
            else:
                return response
        except Exception as e:
            click.echo(e, err=True)
            sys.exit(1)

    def cmd_update(self, uuid, tags=None, clear_tags=None, clear_all_tags=False, wait=False, **kwargs):
            try:
                with Spinner(text=f"Querying by {self.resource_uuid_name} {uuid}"):
                    self.get_client_resource().get_by_uuid(uuid=uuid)

            except CloudscaleApiException as e:
                results = self.cmd_get_by_name(name=uuid)
                if not results:
                    if self.resource_name_key:
                        msg = f"No resource found for {self.cloud_resource_name} having {self.resource_uuid_name} or {self.resource_name_key}: {uuid}"
                    else:
                        msg = f"No resource found for {self.cloud_resource_name} having {self.resource_uuid_name}: {uuid}"
                    click.echo(msg, err=True)
                    sys.exit(1)

                if len(results) > 1:
                    click.echo(f"Error: More than one resource found for {self.cloud_resource_name} having name: {uuid}. Please use {self.resource_uuid_name} to select the resource.", err=True)
                    sys.exit(1)

                # Single resource found, remember identifier
                uuid = results[0]['href'].split('/')[-1]

            try:
                with Spinner(text=f"Processing tags"):
                    if any([clear_all_tags, tags, clear_tags]):
                        _tags = dict()
                        if not clear_all_tags:
                            response = self.get_client_resource().get_by_uuid(uuid=uuid)
                            _tags = response.get('tags', dict()).copy()
                            for k in clear_tags:
                                _tags.pop(k, None)

                        if tags:
                            try:
                                _tags.update(tags_to_dict(tags))
                            except ValueError as e:
                                click.echo(e, err=True)
                                sys.exit(1)
                    else:
                        _tags = None


                with Spinner(text=f"Updating by {self.resource_uuid_name} {uuid}"):
                    self.get_client_resource().update(
                        uuid=uuid,
                        tags=_tags,
                        **kwargs,
                    )

                if wait:
                    response = self.wait_for_status(uuid=uuid)
                else:
                    with Spinner(text=f"Querying {uuid}"):
                        response = self.get_client_resource().get_by_uuid(uuid=uuid)

                click.echo(self._format_output(response))
            except Exception as e:
                click.echo(e, err=True)
                sys.exit(1)

    def cmd_delete(self, uuid, force=False, skip_query=False):
        try:
            if not skip_query:
                try:
                    with Spinner(text=f"Querying by {self.resource_uuid_name} {uuid}"):
                        response = self.get_client_resource().get_by_uuid(uuid=uuid)
                except CloudscaleApiException as e:
                    results = self.cmd_get_by_name(name=uuid)
                    if not results:
                        if self.resource_name_key:
                            msg = f"No resource found for {self.cloud_resource_name} having {self.resource_uuid_name} or {self.resource_name_key}: {uuid}"
                        else:
                            msg = f"No resource found for {self.cloud_resource_name} having {self.resource_uuid_name}: {uuid}"
                        click.echo(msg, err=True)
                        sys.exit(1)

                    if len(results) > 1:
                        click.echo(f"Error: More than one resource found for {self.cloud_resource_name} having name: {uuid}", err=True)
                        sys.exit(1)

                    # Single resource found, remember identifier
                    response = results[0]
                    uuid = results[0]['href'].split('/')[-1]

                click.echo(self._format_output(response))

            if not force:
                click.confirm('Do you want to delete?', abort=True)
            with Spinner(text=f"Deleting by {self.resource_uuid_name} {uuid}"):
                self.get_client_resource().delete(uuid)
            click.echo(f"{uuid} deleted!")
        except Exception as e:
            click.echo(e, err=True)
            sys.exit(1)

    def cmd_act(self, action, uuid, wait=False):
        with Spinner(text=f"Processing"):
            try:
                with Spinner(text=f"Querying by {self.resource_uuid_name} {uuid}"):
                    self.get_client_resource().get_by_uuid(uuid=uuid)

            except CloudscaleApiException as e:
                results = self.cmd_get_by_name(name=uuid)
                if not results:
                    if self.resource_name_key:
                        msg = f"No resource found for {self.cloud_resource_name} having {self.resource_uuid_name} or {self.resource_name_key}: {uuid}"
                    else:
                        msg = f"No resource found for {self.cloud_resource_name} having {self.resource_uuid_name}: {uuid}"
                    click.echo(msg, err=True)
                    sys.exit(1)

                if len(results) > 1:
                    click.echo(f"Error: More than one resource found for {self.cloud_resource_name} having name: {uuid}. Please use {self.resource_uuid_name} to select the resource.", err=True)
                    sys.exit(1)

                # Single resource found, remember identifier
                uuid = results[0]['href'].split('/')[-1]

            try:
                with Spinner(text=f"{action} {uuid}"):
                    getattr(self.get_client_resource(), action)(uuid)

                if wait:
                    response = self.wait_for_status(uuid=uuid)
                else:
                    with Spinner(text=f"Querying {uuid}"):
                        response = self.get_client_resource().get_by_uuid(uuid=uuid)
                click.echo(self._format_output(response))
            except Exception as e:
                click.echo(e, err=True)
                sys.exit(1)

    def wait_for_status(self, uuid, status = "changing", max_sleep = 4, retries = 30, path = ""):
        with Spinner(text=f"Waiting for status {uuid}: ...") as sp:
            for retry in range(0, retries):
                response = self.get_client_resource().get_by_uuid(uuid=uuid, path=path)
                if response['status'] != status:
                    break
                sp.text = f"Waiting for {uuid} to finish, current status: {response['status']} { retry * '.'}"

                # Exponential wait...
                sleep = 2 ** retry
                if sleep > max_sleep:
                    sleep = max_sleep
                time.sleep(sleep)
            else:
                sp.text = f"Waiting for status {uuid} timed out."
                time.sleep(1)
        return response
