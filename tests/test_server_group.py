from cloudscale import CLOUDSCALE_API_ENDPOINT
from cloudscale_cli.cli import cli
import responses
import click
from click.testing import CliRunner

SERVER_GROUP_RESP = {
    "href": "https://api.cloudscale.ch/v1/server-groups/e3b63018-fad6-45f2-9f57-3ea0da726d8c",
    "uuid": "e3b63018-fad6-45f2-9f57-3ea0da726d8c",
    "name": "load balancers",
    "type": "anti-affinity",
    "servers": [
        {
            "href": "https://api.cloudscale.ch/v1/server-groups/32d2f586-14ff-4da9-81df-134ca45d635f",
            "uuid": "32d2f586-14ff-4da9-81df-134ca45d635f",
            "name": "tesla"
        },
        {
            "href": "https://api.cloudscale.ch/v1/server-groups/375870c2-d4ee-49af-a048-efcf59ef14ef",
            "uuid": "375870c2-d4ee-49af-a048-efcf59ef14ef",
            "name": "edison"
        }
    ],
    "zone": {
        "slug": "rma1"
    },
    "tags": {}
}

@responses.activate
def test_server_groups_get_all():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/server-groups',
        json=[SERVER_GROUP_RESP],
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/server-groups',
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a',
        'token',
        'server-group',
        'list',
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a',
        'token',
        '-o',
        'json',
        'server-group',
        'list',
    ])
    assert result.exit_code > 0

@responses.activate
def test_server_groups_get_by_uuid():
    uuid = "e3b63018-fad6-45f2-9f57-3ea0da726d8c"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/server-groups/' + uuid,
        json=SERVER_GROUP_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/server-groups/' + uuid,
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'show',
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        '-o', 'json',
        'server-group',
        'show',
        uuid,
    ])
    assert result.exit_code > 0

@responses.activate
def test_server_groups_delete():
    uuid = "e3b63018-fad6-45f2-9f57-3ea0da726d8c"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/server-groups/' + uuid,
        json=SERVER_GROUP_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/server-groups/unknown',
        json=SERVER_GROUP_RESP,
        status=200)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_ENDPOINT + '/server-groups/' + uuid,
        status=204)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_ENDPOINT + '/server-groups/unknown',
        json={
            "detail": "Not found."
        },
        status=404)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'delete',
        uuid,
    ])
    assert result.exit_code == 1
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'delete',
        '--force',
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'delete',
        '--force',
        'unknown',
    ])
    assert result.exit_code > 0

@responses.activate
def test_server_groups_create():
    name = "load balancers"
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/server-groups',
        json=SERVER_GROUP_RESP,
        status=201)
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/server-groups',
        json=SERVER_GROUP_RESP,
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'create',
        '--name',
        name,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'create',
        '--name',
        name,
    ])
    assert result.exit_code > 0

@responses.activate
def test_server_groups_update():
    uuid = "e3b63018-fad6-45f2-9f57-3ea0da726d8c"
    name = "load balancers"
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/server-groups/' + uuid,
        json=SERVER_GROUP_RESP,
        status=204)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/server-groups/' + uuid,
        json=SERVER_GROUP_RESP,
        status=200)
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/server-groups/' + uuid,
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'update',
        '--name',
        name,
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'update',
        '--name',
        name,
        '--clear-tag',
        'foo',
        uuid,
    ])
    assert result.exit_code > 0

def test_server_group_missing_api_key():
    runner = CliRunner()
    result = runner.invoke(cli, [
        'server-group',
        'list',
    ])
    assert result.exit_code == 1

@responses.activate
def test_invalid_tags_create():
    name = "load balancers"
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/server-groups',
        json=SERVER_GROUP_RESP,
        status=201)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'create',
        '--name',
        name,
        '--tag',
        'foo',
    ])
    assert result.exit_code == 1

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'create',
        '--name',
        name,
        '--tag',
        'foo=',
    ])
    assert result.exit_code == 0

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'create',
        '--name',
        name,
        '--tag',
        'foo=bar=',
    ])
    assert result.exit_code == 0


@responses.activate
def test_invalid_tags_update():
    uuid = "e3b63018-fad6-45f2-9f57-3ea0da726d8c"
    name = "load balancers"
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/server-groups/' + uuid,
        json=SERVER_GROUP_RESP,
        status=204)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/server-groups/' + uuid,
        json=SERVER_GROUP_RESP,
        status=200)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'update',
        '--name',
        name,
        uuid,
        '--tag',
        'foo',
    ])
    assert result.exit_code == 1

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'update',
        '--name',
        name,
        uuid,
        '--tag',
        'foo=',
    ])
    assert result.exit_code == 0

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'server-group',
        'update',
        '--name',
        name,
        uuid,
        '--tag',
        'foo=bar=',
    ])
    assert result.exit_code == 0
