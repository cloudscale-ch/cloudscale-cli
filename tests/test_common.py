import pytest
from click.testing import CliRunner

from cloudscale_cli.cli import cli

COMMANDS = [
    "custom-image",
    "flavor",
    "floating-ip",
    "image",
    "network",
    "objects-user",
    "region",
    "server",
    "server-group",
    "subnet",
    "volume",
]


def test_help_lists_all_commands():
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    for command in COMMANDS:
        assert f"\n  {command}\n" in result.output


def test_no_args_shows_help():
    result = CliRunner().invoke(cli, [])
    # Click reports a missing command as a usage error.
    assert result.exit_code == 2
    assert "Usage: cli [OPTIONS] COMMAND [ARGS]..." in result.output


@pytest.mark.parametrize("command", COMMANDS)
def test_command_help(command):
    result = CliRunner().invoke(cli, [command, "--help"])
    assert result.exit_code == 0
    assert "list" in result.output


def test_unknown_command():
    result = CliRunner().invoke(cli, ["nope"])
    assert result.exit_code == 2
