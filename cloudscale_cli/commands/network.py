import click

@click.group()
@click.pass_context
def network(ctx):
    ctx.obj.cloud_resource_name = "network"
    ctx.obj.headers = [
        'name',
        'created_at',
        'zone',
        'tags',
        'uuid',
    ]

@click.option('--filter-tag')
@click.option('--filter-json')
@click.option('--delete', is_flag=True)
@click.option('--force', is_flag=True)
@network.command("list")
@click.pass_obj
def cmd_list(cloudscale, filter_tag, filter_json, delete, force):
    cloudscale.cmd_list(
        filter_tag=filter_tag,
        filter_json=filter_json,
        delete=delete,
        force=force,
    )

@click.argument('uuid', required=True)
@network.command("show")
@click.pass_obj
def cmd_show(cloudscale, uuid):
    cloudscale.cmd_show(
        uuid=uuid,
    )

@click.option('--name', required=True)
@click.option('--zone')
@click.option('--mtu', type=int, default=9000, show_default=True)
@click.option('--auto-create-ipv4-subnet/--no-auto-create-ipv4-subnet', type=bool, default=True, show_default=True)
@click.option('--tag', 'tags', multiple=True)
@network.command("create")
@click.pass_obj
def cmd_create(cloudscale, name, zone, mtu, auto_create_ipv4_subnet, tags):
    cloudscale.cmd_create(
        name=name,
        zone=zone,
        mtu=mtu,
        auto_create_ipv4_subnet=auto_create_ipv4_subnet,
        tags=tags,
    )

@click.argument('uuid', required=True)
@click.option('--name')
@click.option('--mtu', type=int)
@click.option('--tag', 'tags', multiple=True)
@click.option('--clear-tag', 'clear_tags', multiple=True)
@click.option('--clear-all-tags', is_flag=True)
@network.command("update")
@click.pass_obj
def cmd_update(cloudscale, uuid, name, mtu, tags, clear_tags, clear_all_tags):
    cloudscale.cmd_update(
        uuid=uuid,
        tags=tags,
        clear_tags=clear_tags,
        clear_all_tags=clear_all_tags,
        name=name,
        mtu=mtu,
    )

@click.argument('uuid', required=True)
@click.option('--force', is_flag=True)
@network.command("delete")
@click.pass_obj
def cmd_delete(cloudscale, uuid, force):
    cloudscale.cmd_delete(
        uuid=uuid,
        force=force,
    )
