from cloudscale import CLOUDSCALE_API_ENDPOINT
from cloudscale_cli.cli import cli
import responses
import click
from click.testing import CliRunner

NETWORK_RESP = {
    "href": "https://api.cloudscale.ch/v1/networks/2db69ba3-1864-4608-853a-0771b6885a3a",
    "uuid": "2db69ba3-1864-4608-853a-0771b6885a3a",
    "name": "my-network-name",
    "created_at": "2019-05-29T13:18:42.511407Z",
    "zone": {
        "slug": "lpg1"
    },
    "mtu": 9000,
    "subnets": [
        {
        "href": "https://api.cloudscale.ch/v1/subnets/33333333-1864-4608-853a-0771b6885a3a",
        "uuid": "33333333-1864-4608-853a-0771b6885a3a",
        "cidr": "172.16.0.0/24"
        }
    ],
    "tags": {}
}

@responses.activate
def test_network_get_all():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/networks',
        json=[NETWORK_RESP],
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/networks',
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a',
        'token',
        'network',
        'list',
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a',
        'token',
        'network',
        'list',
    ])
    assert result.exit_code > 0

@responses.activate
def test_network_get_by_uuid():
    uuid = "2db69ba3-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/networks/' + uuid,
        json=NETWORK_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/networks/' + uuid,
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'network',
        'show',
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'network',
        'show',
        uuid,
    ])
    assert result.exit_code > 0

@responses.activate
def test_network_delete():
    uuid = "2db69ba3-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/networks/' + uuid,
        json=NETWORK_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/networks/unknown',
        json=NETWORK_RESP,
        status=200)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_ENDPOINT + '/networks/' + uuid,
        status=204)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_ENDPOINT + '/networks/unknown',
        json={
            "detail": "Not found."
        },
        status=404)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'network',
        'delete',
        uuid,
    ])
    assert result.exit_code == 1
    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'network',
        'delete',
        uuid,
        '--force',
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'network',
        'delete',
        '--force',
        'unknown',
    ])
    assert result.exit_code > 0

@responses.activate
def test_network_create():
    name = "my-network-name"

    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/networks',
        json=NETWORK_RESP,
        status=201)
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/networks',
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'network',
        'create',
        '--name',
        name,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'network',
        'create',
        '--name',
        name,
    ])
    assert result.exit_code > 0


@responses.activate
def test_network_update():
    uuid = "2db69ba3-1864-4608-853a-0771b6885a3a"
    name = "my-network-name"
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/networks/' + uuid,
        json=NETWORK_RESP,
        status=204)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/networks/' + uuid,
        json=NETWORK_RESP,
        status=200)
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/networks/' + uuid,
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'network',
        'update',
        uuid,
        '--name',
        name,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'network',
        'update',
        uuid,
        '--name',
        name,
    ])
    assert result.exit_code > 0


def test_network_missing_api_key():
    runner = CliRunner()
    result = runner.invoke(cli, [
        'network',
        'list',
    ])
    assert result.exit_code == 1
