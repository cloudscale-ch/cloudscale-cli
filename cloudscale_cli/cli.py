"""Entry point of the cloudscale.ch command line interface."""

import click

from . import __version__
from .command import CloudscaleCommand
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
from .output import OUTPUT_FORMATS


class OrderedGroup(click.Group):
    """A click group listing its commands in alphabetical order."""

    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted(self.commands)


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
def cli(
    ctx: click.Context,
    profile: str,
    api_token: str,
    debug: bool,
    output: str,
    verbose: bool,
) -> None:
    ctx.obj = CloudscaleCommand(
        api_token=api_token,
        profile=profile,
        debug=debug,
        output=output,
        verbose=verbose,
    )


for command in (
    custom_image,
    flavor,
    floating_ip,
    image,
    network,
    objects_user,
    region,
    server,
    server_group,
    subnet,
    volume,
):
    cli.add_command(command)
