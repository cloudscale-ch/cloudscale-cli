from click.testing import CliRunner
from cloudscale_cli.cli import cli


def test_list_commands():
    runner = CliRunner()
    result = runner.invoke(cli, [])

    # Since click 8.2, the exit code is 2, when usage is invoked without
    # -h/--help. Since we support older releases as well, it can be one of two.
    assert result.exit_code in (0, 2)

    # This can be avoided by asking for help
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
