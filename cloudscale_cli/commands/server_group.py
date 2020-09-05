import click

@click.group()
@click.pass_context
def server_group(ctx):
    ctx.obj.cloud_resource_name = "server_group"
    ctx.obj.headers = [
        'name',
        'type',
        'servers',
        'zone',
        'tags',
        'uuid',
    ]

@click.option('--filter-tag')
@click.option('--filter-json')
@click.option('--delete', is_flag=True)
@click.option('--force', is_flag=True)
@server_group.command("list")
@click.pass_obj
def cmd_list(cloudscale, filter_tag, filter_json, delete, force):
    cloudscale.cmd_list(
        filter_tag=filter_tag,
        filter_json=filter_json,
        delete=delete,
        force=force,
    )

@click.argument('uuid', required=True)
@server_group.command("show")
@click.pass_obj
def cmd_show(cloudscale, uuid):
    cloudscale.cmd_show(
        uuid=uuid,
    )

@click.option('--name', required=True)
@click.option('--type', 'group_type', default='anti-affinity', show_default=True)
@click.option('--tag', 'tags', multiple=True)
@server_group.command("create")
@click.pass_obj
def cmd_create(cloudscale, name, group_type, tags):
    cloudscale.cmd_create(
        name=name,
        group_type=group_type,
        tags=tags,
    )

@click.argument('uuid', required=True)
@click.option('--name')
@click.option('--tag', 'tags', multiple=True)
@click.option('--clear-tag', 'clear_tags', multiple=True)
@click.option('--clear-all-tags', is_flag=True)
@server_group.command("update")
@click.pass_obj
def cmd_update(cloudscale, uuid, name, tags, clear_tags, clear_all_tags):
    cloudscale.cmd_update(
        uuid=uuid,
        tags=tags,
        clear_tags=clear_tags,
        clear_all_tags=clear_all_tags,
        name=name,
    )

@click.argument('uuid', required=True)
@click.option('--force', is_flag=True)
@server_group.command("delete")
@click.pass_obj
def cmd_delete(cloudscale, uuid, force):
    cloudscale.cmd_delete(
        uuid=uuid,
        force=force,
    )
