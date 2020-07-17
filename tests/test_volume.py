from cloudscale import CLOUDSCALE_API_ENDPOINT
from cloudscale_cli.cli import cli
import responses
import click
from click.testing import CliRunner

VOLUME_RESP = {
    "href": "https://api.cloudscale.ch/v1/volumes/2db69ba3-1864-4608-853a-0771b6885a3a",
    "created_at": "2019-05-29T13:18:42.511407Z",
    "uuid": "2db69ba3-1864-4608-853a-0771b6885a3a",
    "name": "capitano-root",
    "zone": {
        "slug": "lpg1"
    },
    "size_gb": 150,
    "type": "ssd",
    "server_uuids": [
        "9e1f9a7f-e8d0-4086-ad7e-fea161d7c5f7"
    ],
    "tags": {}
}

@responses.activate
def test_volume_get_all():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/volumes',
        json=[VOLUME_RESP],
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/volumes',
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a',
        'token',
        'volume',
        'list',
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a',
        'token',
        'volume',
        'list',
    ])
    assert result.exit_code > 0

@responses.activate
def test_volume_get_by_uuid():
    uuid = "2db69ba3-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/volumes/' + uuid,
        json=VOLUME_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/volumes/' + uuid,
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'volume',
        'show',
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'volume',
        'show',
        uuid,
    ])
    assert result.exit_code > 0

@responses.activate
def test_volume_delete():
    uuid = "2db69ba3-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/volumes/' + uuid,
        json=VOLUME_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/volumes/unknown',
        json=VOLUME_RESP,
        status=200)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_ENDPOINT + '/volumes/' + uuid,
        status=204)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_ENDPOINT + '/volumes/unknown',
        json={
            "detail": "Not found."
        },
        status=404)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'volume',
        'delete',
        uuid,
    ])
    assert result.exit_code == 1
    result = runner.invoke(cli, [
        '-a', 'token',
        'volume',
        'delete',
        '--force',
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'volume',
        'delete',
        '--force',
        'unknown',
    ])
    assert result.exit_code > 0

@responses.activate
def test_volume_create():
    name = "capitano-root"
    size_gb = 150
    server_uuids = "2db69ba3-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/volumes',
        json=VOLUME_RESP,
        status=201)
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/volumes',
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'volume',
        'create',
        '--name',
        name,
        '--server-uuids',
        server_uuids,
        '--size-gb',
        size_gb,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'volume',
        'create',
        '--name',
        name,
        '--server-uuids',
        server_uuids,
        '--size-gb',
        size_gb,
    ])
    assert result.exit_code > 0

@responses.activate
def test_volume_update():
    uuid = "2db69ba3-1864-4608-853a-0771b6885a3a"
    name = "capitano-root"
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/volumes/' + uuid,
        json=VOLUME_RESP,
        status=204)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/volumes/' + uuid,
        json=VOLUME_RESP,
        status=200)
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/volumes/' + uuid,
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'volume',
        'update',
        '--name',
        name,
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'volume',
        'update',
        '--name',
        name,
        uuid,
    ])
    assert result.exit_code > 0

@responses.activate
def test_volume_get_by_uuid_not_found():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/volumes/unknown',
        json={
            "detail": "Not found."
        },
        status=404)

def test_volume_missing_api_key():
    runner = CliRunner()
    result = runner.invoke(cli, [
        'volume',
        'list',
    ])
    assert result.exit_code == 1
