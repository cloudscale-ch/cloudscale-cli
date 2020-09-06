import sys
import click
import jmespath
from cloudscale import Cloudscale, CloudscaleApiException
from ..util import to_table, to_pretty_json, tags_to_dict

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

        self.response_transform_json = None

    def get_client_resource(self):
        return getattr(self._client, self.cloud_resource_name)

    def _format_output(self, response):
        if self._output == "json":
            return to_pretty_json(response)
        else:
            if isinstance(response, dict):
                response = [response]
            return to_table(response, self.headers, self.response_transform_json)

    def cmd_list(self, filter_tag=None, filter_json=None, action=None, delete=False, force=False):
        if action and delete:
            click.echo("Error: --action and --delete are mutually exclusive", err=True)
            sys.exit(1)
        try:
            with Spinner(text="Querying"):
                response = self.get_client_resource().get_all(filter_tag)
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
                    with Spinner(text="Querying"):
                        response = self.get_client_resource().get_all(filter_tag)
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
            with Spinner(text=f"Querying by UUID {uuid}"):
                response = self.get_client_resource().get_by_uuid(uuid)
            click.echo(self._format_output(response))
        except CloudscaleApiException as e:
            results = self.cmd_get_by_name(name=uuid)
            if not results:
                if self.resource_name_key:
                    msg = f"No resource found for {self.cloud_resource_name} having UUID or {self.resource_name_key}: {uuid}"
                else:
                    msg = f"No resource found for {self.cloud_resource_name} having UUID: {uuid}"
                click.echo(msg, err=True)
                sys.exit(1)
            click.echo(self._format_output(results))
        except Exception as e:
            click.echo(e, err=True)
            sys.exit(1)

    def cmd_create(self, silent=False, **kwargs):
        try:
            if 'tags' in kwargs:
                try:
                    kwargs['tags'] = tags_to_dict(kwargs['tags'])
                except ValueError as e:
                    click.echo(e, err=True)
                    sys.exit(1)
            with Spinner(text="Creating"):
                response = self.get_client_resource().create(**kwargs)
            if not silent:
                click.echo(self._format_output(response))
            else:
                return response
        except Exception as e:
            click.echo(e, err=True)
            sys.exit(1)

    def cmd_update(self, uuid, tags, clear_tags, clear_all_tags, **kwargs):
        with Spinner(text=f"Processing"):
            try:
                with Spinner(text=f"Querying by UUID {uuid}"):
                    self.get_client_resource().get_by_uuid(uuid)

            except CloudscaleApiException as e:
                results = self.cmd_get_by_name(name=uuid)
                if not results:
                    if self.resource_name_key:
                        msg = f"No resource found for {self.cloud_resource_name} having UUID or {self.resource_name_key}: {uuid}"
                    else:
                        msg = f"No resource found for {self.cloud_resource_name} having UUID: {uuid}"
                    click.echo(msg, err=True)
                    sys.exit(1)

                if len(results) > 1:
                    click.echo(f"Error: More than one resource found for {self.cloud_resource_name} having name: {uuid}. Please use UUID to select the resource.", err=True)
                    sys.exit(1)

                # Single resource found, remember UUID
                uuid = results[0]['href'].split('/')[-1]

            try:
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


                with Spinner(text=f"Updating by UUID {uuid}"):
                    self.get_client_resource().update(
                        uuid=uuid,
                        tags=_tags,
                        **kwargs,
                    )
                    response = self.get_client_resource().get_by_uuid(uuid=uuid)
                click.echo(self._format_output(response))
            except Exception as e:
                click.echo(e, err=True)
                sys.exit(1)

    def cmd_delete(self, uuid, force=False, skip_query=False):
        try:
            if not skip_query:
                try:
                    with Spinner(text=f"Querying by UUID {uuid}"):
                        response = self.get_client_resource().get_by_uuid(uuid)
                except CloudscaleApiException as e:
                    results = self.cmd_get_by_name(name=uuid)
                    if not results:
                        if self.resource_name_key:
                            msg = f"No resource found for {self.cloud_resource_name} having UUID or {self.resource_name_key}: {uuid}"
                        else:
                            msg = f"No resource found for {self.cloud_resource_name} having UUID: {uuid}"
                        click.echo(msg, err=True)
                        sys.exit(1)

                    if len(results) > 1:
                        click.echo(f"Error: More than one resource found for {self.cloud_resource_name} having name: {uuid}", err=True)
                        sys.exit(1)

                    # Single resource found, remember UUID
                    response = results[0]
                    uuid = results[0]['href'].split('/')[-1]

                click.echo(self._format_output(response))

            if not force:
                click.confirm('Do you want to delete?', abort=True)
            with Spinner(text=f"Deleting by UUID {uuid}"):
                self.get_client_resource().delete(uuid)
            click.echo(f"{uuid} deleted!")
        except Exception as e:
            click.echo(e, err=True)
            sys.exit(1)

    def cmd_act(self, action, uuid):
        with Spinner(text=f"Processing"):
            try:
                with Spinner(text=f"Querying by UUID {uuid}"):
                    self.get_client_resource().get_by_uuid(uuid)

            except CloudscaleApiException as e:
                results = self.cmd_get_by_name(name=uuid)
                if not results:
                    if self.resource_name_key:
                        msg = f"No resource found for {self.cloud_resource_name} having UUID or {self.resource_name_key}: {uuid}"
                    else:
                        msg = f"No resource found for {self.cloud_resource_name} having UUID: {uuid}"
                    click.echo(msg, err=True)
                    sys.exit(1)

                if len(results) > 1:
                    click.echo(f"Error: More than one resource found for {self.cloud_resource_name} having name: {uuid}. Please use UUID to select the resource.", err=True)
                    sys.exit(1)

                # Single resource found, remember UUID
                uuid = results[0]['href'].split('/')[-1]

            try:
                with Spinner(text=f"{action} {uuid}"):
                    getattr(self.get_client_resource(), action)(uuid)

                with Spinner(text=f"Querying {uuid}"):
                    response = self.get_client_resource().get_by_uuid(uuid)
                click.echo(self._format_output(response))
            except Exception as e:
                click.echo(e, err=True)
                sys.exit(1)
