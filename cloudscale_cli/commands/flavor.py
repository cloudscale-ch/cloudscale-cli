import click

@click.group()
@click.pass_context
def flavor(ctx):
    ctx.obj.cloud_resource_name = "flavor"
    ctx.obj.headers = [
        'name',
        'vcpu_count',
        'memory_gb',
        'slug',
        'zones',
    ]

@click.option('--filter-json')
@flavor.command("list")
@click.pass_obj
def cmd_list(cloudscale, filter_json):
    cloudscale.cmd_list(
        filter_json=filter_json,
    )
