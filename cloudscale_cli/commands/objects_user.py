import click

@click.group()
@click.pass_context
def objects_user(ctx):
    ctx.obj.cloud_resource_name = "objects_user"
    ctx.obj.headers = [
        'display_name',
        'tags',
        'access_key',
        'secret_key',
        'id',
    ]
    ctx.obj.resource_name_key = 'display_name'
    ctx.obj.response_transform_json = '''
        [].{
            "display_name": display_name,
            "access_key": keys[].access_key,
            "secret_key": keys[].secret_key,
            "tags": tags,
            "id": id
            }
    '''
@click.option('--filter-tag')
@click.option('--filter-json')
@click.option('--delete', is_flag=True)
@click.option('--force', is_flag=True)
@objects_user.command("list")
@click.pass_obj
def cmd_list(cloudscale, filter_tag, filter_json, delete, force):
    cloudscale.cmd_list(
        filter_tag=filter_tag,
        filter_json=filter_json,
        delete=delete,
        force=force,
    )

@click.argument('uuid', required=True)
@objects_user.command("show")
@click.pass_obj
def cmd_show(cloudscale, uuid):
    cloudscale.cmd_show(
        uuid=uuid,
    )

@click.option('--display-name', required=True)
@click.option('--tag', 'tags', multiple=True)
@objects_user.command("create")
@click.pass_obj
def cmd_create(cloudscale, display_name, tags):
    cloudscale.cmd_create(
        display_name=display_name,
        tags=tags
    )

@click.argument('uuid', required=True)
@click.option('--display-name')
@click.option('--tag', 'tags', multiple=True)
@click.option('--clear-tag', 'clear_tags', multiple=True)
@click.option('--clear-all-tags', is_flag=True)
@objects_user.command("update")
@click.pass_obj
def cmd_update(cloudscale, uuid, display_name, tags, clear_tags, clear_all_tags):
    cloudscale.cmd_update(
        uuid=uuid,
        tags=tags,
        clear_tags=clear_tags,
        clear_all_tags=clear_all_tags,
        display_name=display_name
    )

@click.argument('uuid', required=True)
@click.option('--force', is_flag=True)
@objects_user.command("delete")
@click.pass_obj
def cmd_delete(cloudscale, uuid, force):
    cloudscale.cmd_delete(
        uuid=uuid,
        force=force,
    )
