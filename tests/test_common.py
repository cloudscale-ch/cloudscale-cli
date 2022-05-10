from click.testing import CliRunner
from cloudscale_cli.cli import cli


def test_list_commands():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
