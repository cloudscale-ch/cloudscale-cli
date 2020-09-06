import sys
import click
import uuid
import jmespath
import os
from cloudscale import CloudscaleApiException

@click.group()
@click.pass_context
def server(ctx):

    headers = [
        'name',
        'status',
        'zone',
        'tags',
        'uuid',
    ]

    verbose_headers = [
        'name',
        'image',
        'flavor',
        'status',
        'zone',
        'public_ips',
        'private_ips',
        'server_groups',
        'volumes',
        'tags',
        'uuid',
    ]

    ctx.obj.cloud_resource_name = "server"
    ctx.obj.headers = verbose_headers if ctx.obj.verbose else headers
    ctx.obj.response_transform_json = '''
        [].{
            "name": name,
            "image": image.slug,
            "flavor": flavor.slug,
            "tags": tags,
            "server_groups": server_groups,
            "volumes": volumes[].name,
            "public_ips": interfaces[?type=='public'].addresses[].address,
            "private_ips": interfaces[?type=='private'].addresses[].address,
            "zone": zone.slug,
            "status": status,
            "uuid": uuid
            }
    '''

@click.option('--filter-tag')
@click.option('--filter-json')
@click.option('--action', type=click.Choice(['start', 'stop', 'reboot']))
@click.option('--delete', is_flag=True)
@click.option('--force', is_flag=True)
@server.command("list")
@click.pass_obj
def cmd_list(cloudscale, filter_tag, filter_json, action, delete, force):
    cloudscale.cmd_list(
        filter_tag=filter_tag,
        filter_json=filter_json,
        action=action,
        delete=delete,
        force=force,
    )

@click.argument('uuid', required=True)
@server.command("show")
@click.pass_obj
def cmd_show(cloudscale, uuid):
    cloudscale.cmd_show(
        uuid=uuid,
    )

@click.option('--count', type=click.IntRange(1, 10), default=1, show_default=True)
@click.option('--name', required=True)
@click.option('--flavor', required=True)
@click.option('--image', required=True)
@click.option('--zone')
@click.option('--volume-size', type=int, default=10)
@click.option('--volume', 'volumes', multiple=True)
@click.option('--interface', 'interfaces', multiple=True)
@click.option('--ssh-key', 'ssh_keys', multiple=True)
@click.option('--password')
@click.option('--use-public-network/--no-use-public-network', default=True)
@click.option('--use-private-network/--no-use-private-network', default=False)
@click.option('--use-ipv6/--no-use-ipv6', default=True)
@click.option('--server-group', 'server_groups', multiple=True)
@click.option('--user-data')
@click.option('--tag', 'tags', multiple=True)
@server.command("create")
@click.pass_obj
def cmd_create(
    cloudscale,
    name,
    flavor,
    image,
    zone,
    volume_size,
    volumes,
    interfaces,
    ssh_keys,
    password,
    use_public_network,
    use_private_network,
    use_ipv6,
    server_groups,
    user_data,
    tags,
    count,
):
    servers_created = list()
    while len(servers_created) < count:
        uid = str(uuid.uuid4()).split('-')[0]
        counter = len(servers_created) + 1
        try:
            server_name = name.format(uid=uid, counter=counter)
        except KeyError as e:
            click.echo(f"Error: Could not format name '{name}': {e}", err=True)
            sys.exit(1)

        s = cloudscale.cmd_create(
            silent=True,
            name=server_name,
            flavor=flavor,
            image=image,
            zone=zone,
            volume_size=volume_size,
            volumes=volumes or None,
            interfaces=interfaces or None,
            ssh_keys=ssh_keys or None,
            password=password,
            use_public_network=use_public_network,
            use_private_network=use_private_network,
            use_ipv6=use_ipv6,
            server_groups=server_groups or None,
            user_data=user_data,
            tags=tags,
        )
        servers_created.append(s)
    click.echo(cloudscale._format_output(servers_created))

@click.argument('uuid', required=True)
@click.option('--name')
@click.option('--flavor')
@click.option('--interface', 'interfaces', multiple=True)
@click.option('--tag', 'tags', multiple=True)
@click.option('--clear-tag', 'clear_tags', multiple=True)
@click.option('--clear-all-tags', is_flag=True)
@server.command("update")
@click.pass_obj
def cmd_update(cloudscale, uuid, name, flavor, interfaces, tags, clear_tags, clear_all_tags):
    cloudscale.cmd_update(
        uuid=uuid,
        tags=tags,
        clear_tags=clear_tags,
        clear_all_tags=clear_all_tags,
        name=name,
        flavor=flavor,
        interfaces=interfaces or None,
    )

@click.argument('uuid', required=True)
@click.option('--force', is_flag=True)
@server.command("delete")
@click.pass_obj
def cmd_delete(cloudscale, uuid, force):
    cloudscale.cmd_delete(
        uuid=uuid,
        force=force,
    )

@click.argument('uuid', required=True)
@server.command("start")
@click.pass_obj
def cmd_start(cloudscale, uuid):
    cloudscale.cmd_act(
        action="start",
        uuid=uuid,
    )

@click.argument('uuid', required=True)
@server.command("stop")
@click.pass_obj
def cmd_stop(cloudscale, uuid):
    cloudscale.cmd_act(
        action="stop",
        uuid=uuid,
    )

@click.argument('uuid', required=True)
@server.command("reboot")
@click.pass_obj
def cmd_reboot(cloudscale, uuid):
    cloudscale.cmd_act(
        action="reboot",
        uuid=uuid,
    )

@click.argument('uuid', required=True)
@click.option('--interface', type=click.Choice(['public', 'private']), default='public', show_default=True)
@server.command("ssh")
@click.pass_obj
def cmd_ssh(cloudscale, uuid, interface):
    try:
        response = cloudscale.get_client_resource().get_by_uuid(uuid)
    except CloudscaleApiException as e:
        results = cloudscale.cmd_get_by_name(name=uuid)
        if not results:
            if cloudscale.resource_name_key:
                msg = f"No resource found for {cloudscale.cloud_resource_name} having UUID or {cloudscale.resource_name_key}: {uuid}"
            else:
                msg = f"No resource found for {cloudscale.cloud_resource_name} having UUID: {uuid}"
            click.echo(msg, err=True)
            sys.exit(1)

        if len(results) > 1:
            click.echo(f"Error: More than one resource found for {cloudscale.cloud_resource_name} having name: {uuid}. Use UUID to update.", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(e, err=True)
        sys.exit(1)

    try:
        response = results[0]
        filter_json = '''
            {
            "public": interfaces[?type=='public'].addresses[0].address,
            "private": interfaces[?type=='private'].addresses[0].address,
            "username": image.default_username
            }
        '''
        response = jmespath.search(filter_json, response)
        for host in response[interface]:
            ssh_cmd = f"ssh {response['username']}@{host}"
            os.system(ssh_cmd)
            break
        else:
            click.echo(f"No IP on interface found: {interface}", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(e, err=True)
        sys.exit(1)
