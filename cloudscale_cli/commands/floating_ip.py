import click

@click.group()
@click.pass_context
def floating_ip(ctx):
    ctx.obj.cloud_resource_name = "floating_ip"
    ctx.obj.headers = [
        'network',
        'ip_version',
        'server',
        'reverse_ptr',
        'type',
        'region',
        'tags',
    ]
    ctx.obj.resource_name_key = None

@click.option('--filter-tag')
@click.option('--filter-json')
@click.option('--delete', is_flag=True)
@click.option('--force', is_flag=True)
@floating_ip.command("list")
@click.pass_obj
def cmd_list(cloudscale, filter_tag, filter_json, delete, force):
    cloudscale.cmd_list(
        filter_tag=filter_tag,
        filter_json=filter_json,
        delete=delete,
        force=force,
    )

@click.argument('network-id', required=True)
@floating_ip.command("show")
@click.pass_obj
def cmd_show(cloudscale, network_id):
    cloudscale.cmd_show(
        uuid=network_id,
    )

@click.option('--ip-version', type=int, default=4, show_default=True)
@click.option('--server-uuid', '--server')
@click.option('--prefix-length', type=int)
@click.option('--reverse-ptr')
@click.option('--type', 'scope', type=click.Choice(['regional', 'global']), default='regional', show_default=True)
@click.option('--region')
@click.option('--tag', 'tags', multiple=True)
@floating_ip.command("create")
@click.pass_obj
def cmd_create(cloudscale, ip_version, server_uuid, prefix_length, reverse_ptr, scope, region, tags):
    if not prefix_length:
        if ip_version == 6:
            prefix_length = 128
        else:
            prefix_length = 32

    cloudscale.cmd_create(
        ip_version=ip_version,
        server_uuid=server_uuid,
        prefix_length=prefix_length,
        reverse_ptr=reverse_ptr,
        scope=scope,
        region=region,
        tags=tags,
    )

@click.argument('network-id', required=True)
@click.option('--server-uuid', '--server')
@click.option('--reverse-ptr')
@click.option('--tag', 'tags', multiple=True)
@click.option('--clear-tag', 'clear_tags', multiple=True)
@click.option('--clear-all-tags', is_flag=True)
@floating_ip.command("update")
@click.pass_obj
def cmd_update(cloudscale, network_id, server_uuid, reverse_ptr, tags, clear_tags, clear_all_tags):
    cloudscale.cmd_update(
        uuid=network_id,
        tags=tags,
        clear_tags=clear_tags,
        clear_all_tags=clear_all_tags,
        server_uuid=server_uuid,
        reverse_ptr=reverse_ptr,
    )

@click.argument('network-id', required=True)
@click.option('--force', is_flag=True)
@floating_ip.command("delete")
@click.pass_obj
def cmd_delete(cloudscale, network_id, force):
    cloudscale.cmd_delete(
        uuid=network_id,
        force=force,
    )
