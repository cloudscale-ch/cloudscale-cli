import click
from cloudscale_cli.cli import cli
from click.testing import CliRunner

def test_version():

    runner = CliRunner()
    result = runner.invoke(cli, [
        '--version',
    ])
    assert result.exit_code == 0
