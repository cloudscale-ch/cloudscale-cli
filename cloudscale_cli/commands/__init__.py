import sys
import click
import jmespath
from cloudscale import Cloudscale, CloudscaleApiException, CloudscaleException
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

    def __init__(self, cloud_resource_name=None, api_token=None, profile=None, debug=False, output="table", headers=[]):
        try:
            self._client = Cloudscale(
                api_token=api_token,
                profile=profile,
                debug=debug
            )
        except CloudscaleException as e:
            click.echo(e, err=True)
            sys.exit(1)

        self._output = output

        self.cloud_resource_name = cloud_resource_name
        self.headers = headers

    def get_client_resource(self):
        return getattr(self._client, self.cloud_resource_name)

    def _format_output(self, response):
        if self._output == "json":
            return to_pretty_json(response)
        else:
            if isinstance(response, dict):
                response = [response]
            return to_table(response, self.headers)

    def cmd_list(self, filter_tag=None, filter_json=None, action=None, delete=False, uuid='uuid'):
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
            click.echo(self._format_output(response))
            if delete:
                click.confirm(f"Do you want to delete?", abort=True)
                for r in response:
                    if uuid not in r:
                        click.echo("No UUID found, could not delete.", err=True)
                        sys.exit(1)
                    self.cmd_delete(uuid=r[uuid], force=True, skip_query=True)
            elif action:
                click.confirm(f"Do you want to {action}?", abort=True)
                for r in response:
                    if uuid not in r:
                        click.echo(f"No UUID found, could not {action}.", err=True)
                        sys.exit(1)
                    with Spinner(text=f"{action.capitalize()} {r[uuid]}"):
                        getattr(self.get_client_resource(), action)(r[uuid])
                with Spinner(text="Querying"):
                    response = self.get_client_resource().get_all(filter_tag)
                click.echo(self._format_output(response))
        except CloudscaleApiException as e:
            click.echo(e, err=True)
            sys.exit(1)

    def cmd_show(self, uuid):
        try:
            with Spinner(text=f"Querying {uuid}"):
                response = self.get_client_resource().get_by_uuid(uuid)
            click.echo(self._format_output(response))
        except CloudscaleApiException as e:
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
        except CloudscaleApiException as e:
            click.echo(e, err=True)
            sys.exit(1)

    def cmd_update(self, uuid, tags, clear_tags, clear_all_tags, **kwargs):
        try:
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

            with Spinner(text=f"Updating {uuid}"):
                self.get_client_resource().update(
                    uuid=uuid,
                    tags=_tags,
                    **kwargs,
                )
                response = self.get_client_resource().get_by_uuid(uuid=uuid)
            click.echo(self._format_output(response))
        except CloudscaleApiException as e:
            click.echo(e, err=True)
            sys.exit(1)

    def cmd_delete(self, uuid, force=False, skip_query=False):
        try:
            if not skip_query:
                with Spinner(text=f"Querying {uuid}"):
                    response = self.get_client_resource().get_by_uuid(uuid)
                click.echo(self._format_output(response))
            if not force:
                click.confirm('Do you want to delete?', abort=True)
            with Spinner(text=f"Deleting {uuid}"):
                self.get_client_resource().delete(uuid)
            click.echo(f"{uuid} deleted!")
        except CloudscaleApiException as e:
            click.echo(e, err=True)
            sys.exit(1)

    def cmd_act(self, action, uuid):
        try:
            with Spinner(text=f"{action} {uuid}"):
                getattr(self.get_client_resource(), action)(uuid)

            with Spinner(text=f"Querying {uuid}"):
                response = self.get_client_resource().get_by_uuid(uuid)
            click.echo(self._format_output(response))
        except CloudscaleApiException as e:
            click.echo(e, err=True)
            sys.exit(1)
