import click

@click.group()
@click.pass_context
def subnet(ctx):
    ctx.obj.cloud_resource_name = "subnet"
    ctx.obj.headers = [
        'uuid',
        'cidr',
        'network',
        'gateway_address',
        'dns_servers',
        'tags',
    ]
    ctx.obj.resource_name_key = None

@click.option('--filter-tag')
@click.option('--filter-json')
@click.option('--delete', is_flag=True)
@click.option('--force', is_flag=True)
@subnet.command("list")
@click.pass_obj
def cmd_list(cloudscale, filter_tag, filter_json, delete, force):
    cloudscale.cmd_list(
        filter_tag=filter_tag,
        filter_json=filter_json,
        delete=delete,
        force=force,
    )

@click.argument('uuid', required=True)
@subnet.command("show")
@click.pass_obj
def cmd_show(cloudscale, uuid):
    cloudscale.cmd_show(
        uuid=uuid,
    )

@click.option('--cidr', required=True)
@click.option('--network-uuid', required=True)
@click.option('--gateway-address')
@click.option('--dns-server', 'dns_servers', multiple=True)
@click.option('--tag', 'tags', multiple=True)
@subnet.command("create")
@click.pass_obj
def cmd_create(cloudscale, cidr, network_uuid, gateway_address, dns_servers, tags):
    cloudscale.cmd_create(
        cidr=cidr,
        network_uuid=network_uuid,
        gateway_address=gateway_address,
        dns_servers=dns_servers or None,
        tags=tags,
    )

@click.argument('uuid', required=True)
@click.option('--gateway-address')
@click.option('--dns-server', 'dns_servers', multiple=True)
@click.option('--tag', 'tags', multiple=True)
@click.option('--clear-tag', 'clear_tags', multiple=True)
@click.option('--clear-all-tags', is_flag=True)
@subnet.command("update")
@click.pass_obj
def cmd_update(cloudscale, uuid, gateway_address, dns_servers, tags, clear_tags, clear_all_tags):
    cloudscale.cmd_update(
        uuid=uuid,
        gateway_address=gateway_address,
        dns_servers=dns_servers or None,
        tags=tags,
        clear_tags=clear_tags,
        clear_all_tags=clear_all_tags,
    )

@click.argument('uuid', required=True)
@click.option('--force', is_flag=True)
@subnet.command("delete")
@click.pass_obj
def cmd_delete(cloudscale, uuid, force):
    cloudscale.cmd_delete(
        uuid=uuid,
        force=force,
    )
