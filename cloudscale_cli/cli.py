import click

from .commands import OUTPUT_FORMATS, CloudscaleCommand
from .commands.custom_image import custom_image
from .commands.flavor import flavor
from .commands.floating_ip import floating_ip
from .commands.image import image
from .commands.network import network
from .commands.objects_user import objects_user
from .commands.region import region
from .commands.server import server
from .commands.server_group import server_group
from .commands.subnet import subnet
from .commands.volume import volume
from .util import OrderedGroup
from .version import __version__


@click.group(
    cls=OrderedGroup,
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
@click.version_option(__version__, "--version")
@click.option("--api-token", "-a", envvar="CLOUDSCALE_API_TOKEN", help="API token.")
@click.option(
    "--profile", "-p", envvar="CLOUDSCALE_PROFILE", help="Profile used in config file."
)
@click.option(
    "--debug", envvar="CLOUDSCALE_DEBUG", is_flag=True, help="Enables debug log output."
)
@click.option(
    "--output",
    "-o",
    envvar="CLOUDSCALE_OUTPUT",
    type=click.Choice(OUTPUT_FORMATS),
    default="table",
    help="Output format.",
    show_default=True,
)
@click.option(
    "--verbose", "-v", envvar="CLOUDSCALE_VERBOSE", is_flag=True, help="Verbose output."
)
@click.pass_context
def cli(ctx, profile, api_token, debug, output, verbose):
    ctx.obj = CloudscaleCommand(
        api_token=api_token,
        profile=profile,
        debug=debug,
        output=output,
        verbose=verbose,
    )


cli.add_command(custom_image, name='custom-image')
cli.add_command(flavor, name='flavor')
cli.add_command(floating_ip, name='floating-ip')
cli.add_command(image, name='image')
cli.add_command(network, name='network')
cli.add_command(objects_user, name='objects-user')
cli.add_command(region, name='region')
cli.add_command(server_group, name='server-group')
cli.add_command(server, name='server')
cli.add_command(subnet, name='subnet')
cli.add_command(volume, name='volume')
