import click
from .version import __version__
from .util import OrderedGroup
from .commands import CloudscaleCommand, OUTPUT_FORMATS
from .commands.server import server
from .commands.server_group import server_group
from .commands.flavor import flavor
from .commands.floating_ip import floating_ip
from .commands.image import image
from .commands.region import region
from .commands.network import network
from .commands.subnet import subnet
from .commands.volume import volume
from .commands.objects_user import objects_user

@click.group(cls=OrderedGroup, context_settings={
    'help_option_names': ['-h', '--help'],
})
@click.version_option(__version__, '--version')
@click.option('--api-token', '-a', envvar='CLOUDSCALE_API_TOKEN', help="API token.")
@click.option('--profile', '-p', envvar='CLOUDSCALE_PROFILE', help="Profile used in config file.")
@click.option('--debug', envvar='CLOUDSCALE_DEBUG', is_flag=True, help='Enables debug log output.')
@click.option('--output', '-o', envvar='CLOUDSCALE_OUTPUT', type=click.Choice(OUTPUT_FORMATS), default="table", help="Output format.", show_default=True)
@click.option('--verbose', '-v', envvar='CLOUDSCALE_VERBOSE', is_flag=True, help='Verbose output.')
@click.pass_context
def cli(ctx, profile, api_token, debug, output, verbose):
    ctx.obj = CloudscaleCommand(
        api_token=api_token,
        profile=profile,
        debug=debug,
        output=output,
        verbose=verbose,
    )


cli.add_command(server)
cli.add_command(server_group)
cli.add_command(floating_ip)
cli.add_command(flavor)
cli.add_command(image)
cli.add_command(region)
cli.add_command(network)
cli.add_command(subnet)
cli.add_command(volume)
cli.add_command(objects_user)
