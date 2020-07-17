import click
from cloudscale_cli.cli import cli
from click.testing import CliRunner


def test_list_commands():
    runner = CliRunner()
    result = runner.invoke(cli, [
    ])
    assert result.exit_code == 0
