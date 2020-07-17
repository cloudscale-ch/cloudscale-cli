import click

@click.group()
@click.pass_context
def image(ctx):
    ctx.obj.cloud_resource_name = "image"
    ctx.obj.headers = [
        'name',
        'operating_system',
        'default_username',
        'slug',
    ]

@click.option('--filter-json')
@image.command("list")
@click.pass_obj
def cmd_list(cloudscale, filter_json):
    cloudscale.cmd_list(
        filter_json=filter_json,
    )
