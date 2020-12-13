import sys
import time
import click
from . import Spinner

@click.group()
@click.pass_context
def custom_image(ctx):
    headers = [
        'name',
        'slug',
        'created_at',
        'zones',
        'tags',
        'uuid',
    ]
    verbose_headers = [
        'name',
        'slug',
        'created_at',
        'zones',
        'user_data_handling',
        'tags',
        'checksum_md5',
        'checksum_sha256',
        'uuid',
    ]

    ctx.obj.cloud_resource_name = "custom_image"
    ctx.obj.headers = verbose_headers if ctx.obj.verbose else headers
    ctx.obj.response_transform_json = '''
        [].{
            "name": name,
            "slug": slug,
            "user_data_handling": user_data_handling,
            "zones": zones[].slug,
            "tags": tags,
            "uuid": uuid,
            "created_at": created_at,
            "checksum_sha256": checksums.sha256,
            "checksum_md5": checksums.md5
            }
    '''

@click.option('--filter-tag')
@click.option('--filter-json')
@click.option('--delete', is_flag=True)
@click.option('--force', is_flag=True)
@custom_image.command("list")
@click.pass_obj
def cmd_list(cloudscale, filter_tag, filter_json, delete, force):
    cloudscale.cmd_list(
        filter_tag=filter_tag,
        filter_json=filter_json,
        delete=delete,
        force=force,
    )

@click.argument('uuid', required=True)
@custom_image.command("show")
@click.pass_obj
def cmd_show(cloudscale, uuid):
    cloudscale.cmd_show(
        uuid=uuid,
    )

@click.option('--url', required=True)
@click.option('--name', required=True)
@click.option('--slug', required=True)
@click.option('--user-data-handling', type=click.Choice(['pass-through', 'extend-cloud-config']), required=True)
@click.option('--zone', 'zones', multiple=True, required=True)
@click.option('--source-format', type=click.Choice(['raw']), default="raw", show_default=True)
@click.option('--tag', 'tags', multiple=True)
@click.option('--wait', is_flag=True)
@custom_image.command("import")
@click.pass_obj
def cmd_import(cloudscale, url, name, slug, user_data_handling, zones, source_format, tags, wait):
    try:
        tags = cloudscale._handle_tags(tags)
        zones_string = ', '.join(zones)
        msg = f"{url} as {name} into zone: {zones_string}. "

        with Spinner(text="Importing " + msg):
            response = cloudscale.get_client_resource().import_by_url(
                url=url,
                name=name,
                slug=slug,
                user_data_handling=user_data_handling,
                zones=zones,
                source_format=source_format,
                tags=tags,
            )

        if not wait:
            click.echo("Import continues in the background and may take a while.")
            sys.exit(0)

        response = cloudscale.wait_for_status(uuid=response['uuid'],
            status = "in_progress",
            max_sleep = 8,
            retries = 120,
            path = "/import"
        )

        if response.get('status') == "failed":
            click.echo("Import failed.")
            sys.exit(1)

        response = cloudscale.get_client_resource().get_by_uuid(uuid=response['uuid'])
        click.echo(cloudscale._format_output(response))

    except Exception as e:
        click.echo(e, err=True)
        sys.exit(1)

@click.argument('uuid', required=True)
@click.option('--name')
@click.option('--slug')
@click.option('--user-data-handling', type=click.Choice(['pass-through', 'extend-cloud-config']))
@click.option('--tag', 'tags', multiple=True)
@click.option('--clear-tag', 'clear_tags', multiple=True)
@click.option('--clear-all-tags', is_flag=True)
@custom_image.command("update")
@click.pass_obj
def cmd_update(cloudscale, uuid, name, slug, user_data_handling, tags, clear_tags, clear_all_tags):
    cloudscale.cmd_update(
        uuid=uuid,
        tags=tags,
        clear_tags=clear_tags,
        clear_all_tags=clear_all_tags,
        name=name,
        slug=slug,
        user_data_handling=user_data_handling,
    )

@click.argument('uuid', required=True)
@click.option('--force', is_flag=True)
@custom_image.command("delete")
@click.pass_obj
def cmd_delete(cloudscale, uuid, force):
    cloudscale.cmd_delete(
        uuid=uuid,
        force=force,
    )
