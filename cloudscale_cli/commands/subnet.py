import click

@click.group()
@click.pass_context
def subnet(ctx):
    ctx.obj.cloud_resource_name = "subnet"
    ctx.obj.headers = [
        'uuid',
        'cidr',
        'network',
        'tags',
    ]

@click.option('--filter-tag')
@click.option('--filter-json')
@subnet.command("list")
@click.pass_obj
def cmd_list(cloudscale, filter_tag, filter_json):
    cloudscale.cmd_list(
        filter_tag=filter_tag,
        filter_json=filter_json,
    )

@click.argument('uuid', required=True)
@subnet.command("show")
@click.pass_obj
def cmd_show(cloudscale, uuid):
    cloudscale.cmd_show(
        uuid=uuid,
    )
