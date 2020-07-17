import click

@click.group()
@click.pass_context
def region(ctx):
    ctx.obj.cloud_resource_name = "region"
    ctx.obj.headers = [
        'name',
        'vcpu_count',
        'memory_gb',
        'slug',
        'zones',
    ]

@click.option('--filter-json')
@region.command("list")
@click.pass_obj
def cmd_list(cloudscale, filter_json):
    cloudscale.cmd_list(
        filter_json=filter_json,
    )
