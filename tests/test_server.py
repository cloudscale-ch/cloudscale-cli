from cloudscale import CLOUDSCALE_API_ENDPOINT
from cloudscale_cli.cli import cli
import responses
import click
from click.testing import CliRunner

SERVER_RESP = {
    "uuid": "47cec963-fcd2-482f-bdb6-24461b2d47b1",
    "name": "db-master",
    "status": "running",
    "zone": {
        "slug": "lpg1"
    },
    "flavor": {
        "slug": "flex-4",
    },
    "image": {
        "slug": "debian-9",
    },
    "server_groups": [],
    "anti_affinity_with": [],
    "tags": {
        "project": "gemini"
    }
}

@responses.activate
def test_server_get_all():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/servers',
        json=[SERVER_RESP],
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/servers',
        json={
            "detail": "Server error."
        },
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a',
        'token',
        'server',
        'list',
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a',
        'token',
        'server',
        'list',
    ])
    assert result.exit_code > 0

@responses.activate
def test_server_get_all_fitlered():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/servers',
        json=[SERVER_RESP],
        status=200)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a',
        'token',
        'server',
        'list',
        '--filter-tag',
        'project=gemini'
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a',
        'token',
        'server',
        'list',
        '--filter-tag',
        'project'
    ])
    assert result.exit_code == 0

@responses.activate
def test_server_get_by_uuid():
    uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid,
        json=SERVER_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid,
        json={
            "detail": "Server error."
        },
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'show',
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'show',
        uuid,
    ])
    assert result.exit_code > 0

@responses.activate
def test_server_delete():
    uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid,
        json=SERVER_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/servers/unknown',
        json=SERVER_RESP,
        status=200)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid,
        status=204)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_ENDPOINT + '/servers/unknown',
        json={
            "detail": "Not found."
        },
        status=404)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'delete',
        uuid,
    ])
    assert result.exit_code == 1
    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'delete',
        '--force',
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'delete',
        '--force',
        'unknown',
    ])
    assert result.exit_code > 0

def test_server_missing_api_key():
    runner = CliRunner()
    result = runner.invoke(cli, [
        'server',
        'list',
    ])
    assert result.exit_code == 1

@responses.activate
def test_server_create():
    name = "db-master"
    flavor = "flex-4"
    image = "debian9"

    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/servers',
        json=SERVER_RESP,
        status=201)
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/servers',
        json={
            "detail": "Server error."
        },
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'create',
        '--name',
        name,
        '--flavor',
        flavor,
        '--image',
        image
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'create',
        '--name',
        name,
        '--flavor',
        flavor,
        '--image',
        image
    ])
    assert result.exit_code > 0

@responses.activate
def test_server_update():
    uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    name = "db-master"
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid,
        json=SERVER_RESP,
        status=204)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid,
        json=SERVER_RESP,
        status=200)
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid,
        json={
            "detail": "Server error."
        },
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'update',
        '--name',
        name,
        '--tag',
        'project=gemini',
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'update',
        '--name',
        name,
        '--tag',
        'project=gemini',
        uuid,
    ])
    assert result.exit_code > 0

@responses.activate
def test_server_start():
    uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid + '/start',
        status=204)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid,
        json=SERVER_RESP,
        status=200)
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid + '/start',
        json={
            "detail": "Server error."
        },
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'start',
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'start',
        uuid,
    ])
    assert result.exit_code > 0

@responses.activate
def test_server_stop():
    uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid + '/stop',
        status=204)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid,
        json=SERVER_RESP,
        status=200)
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid + '/stop',
        json={
            "detail": "Server error."
        },
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'stop',
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'stop',
        uuid,
    ])
    assert result.exit_code > 0

@responses.activate
def test_server_reboot():
    uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid + '/reboot',
        status=204)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid,
        json=SERVER_RESP,
        status=200)
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/servers/' + uuid + '/reboot',
        json={
            "detail": "Server error."
        },
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'reboot',
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'server',
        'reboot',
        uuid,
    ])
    assert result.exit_code > 0
