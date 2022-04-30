from click.testing import CliRunner
from cloudscale_cli.cli import cli


def test_version():

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--version",
        ],
    )
    assert result.exit_code == 0
