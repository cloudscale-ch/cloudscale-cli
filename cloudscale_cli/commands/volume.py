import click

@click.group()
@click.pass_context
def volume(ctx):
    ctx.obj.cloud_resource_name = "volume"
    ctx.obj.headers = [
        'name',
        'type',
        'size_gb',
        'zone',
        'tags',
        'server_uuids',
        'uuid',
    ]

@click.option('--filter-tag')
@click.option('--filter-json')
@click.option('--delete', is_flag=True)
@click.option('--force', is_flag=True)
@volume.command("list")
@click.pass_obj
def cmd_list(cloudscale, filter_tag, filter_json, delete, force):
    cloudscale.cmd_list(
        filter_tag=filter_tag,
        filter_json=filter_json,
        delete=delete,
        force=force,
    )

@click.argument('uuid', required=True)
@volume.command("show")
@click.pass_obj
def cmd_show(cloudscale, uuid):
    cloudscale.cmd_show(
        uuid=uuid,
    )

@click.option('--name', required=True)
@click.option('--server-uuids', multiple=True, required=True)
@click.option('--size-gb', type=int, required=True)
@click.option('--type', 'volume_type', type=click.Choice(['ssd', 'bulk']), default='ssd', show_default=True)
@click.option('--zone')
@click.option('--tag', 'tags', multiple=True)
@volume.command("create")
@click.pass_obj
def cmd_create(cloudscale, name, server_uuids, size_gb, volume_type, zone, tags):
    cloudscale.cmd_create(
        name=name,
        server_uuids=server_uuids,
        size_gb=size_gb,
        volume_type=volume_type,
        zone=zone,
        tags=tags,
    )

@click.argument('uuid', required=True)
@click.option('--name')
@click.option('--server-uuids', multiple=True)
@click.option('--size-gb', type=int)
@click.option('--tag', 'tags', multiple=True)
@click.option('--clear-tag', 'clear_tags', multiple=True)
@click.option('--clear-all-tags', is_flag=True)
@volume.command("update")
@click.pass_obj
def cmd_update(cloudscale, uuid, name, server_uuids, size_gb, tags, clear_tags, clear_all_tags):
    cloudscale.cmd_update(
        uuid=uuid,
        tags=tags,
        clear_tags=clear_tags,
        clear_all_tags=clear_all_tags,
        name=name,
        server_uuids=server_uuids,
        size_gb=size_gb,
    )

@click.argument('uuid', required=True)
@click.option('--force', is_flag=True)
@volume.command("delete")
@click.pass_obj
def cmd_delete(cloudscale, uuid, force):
    cloudscale.cmd_delete(
        uuid=uuid,
        force=force,
    )
