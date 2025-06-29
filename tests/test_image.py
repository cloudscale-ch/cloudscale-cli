import responses
from click.testing import CliRunner
from cloudscale import CLOUDSCALE_API_URL
from cloudscale_cli.cli import cli

IMAGE_RESP = {
    "slug": "arch-18.06",
    "name": "Arch 18.06",
    "operating_system": "Arch",
    "default_username": "arch",
    "zones": [{"slug": "rma1"}, {"slug": "lpg1"}],
}


@responses.activate
def test_image_get_all():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/images",
        json=[IMAGE_RESP],
        status=200,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/images",
        json={},
        status=500,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "image",
            "list",
        ],
    )
    assert result.exit_code == 0
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "image",
            "list",
        ],
    )
    assert result.exit_code > 0


def test_image_missing_api_key():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "image",
            "list",
        ],
    )
    assert result.exit_code == 1
