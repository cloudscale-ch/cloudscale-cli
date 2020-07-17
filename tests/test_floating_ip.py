from cloudscale import CLOUDSCALE_API_ENDPOINT
from cloudscale_cli.cli import cli
import responses
import click
from click.testing import CliRunner

FLOATING_IP_RESP = {
    "href": "https://api.cloudscale.ch/v1/floating-ips/192.0.2.123",
    "created_at": "2019-05-29T13:18:42.505197Z",
    "network": "192.0.2.123/32",
    "ip_version": 4,
    "server": {
        "href": "https://api.cloudscale.ch/v1/servers/47cec963-fcd2-482f-bdb6-24461b2d47b1",
        "uuid": "47cec963-fcd2-482f-bdb6-24461b2d47b1",
        "name": "db-master"
    },
    "region": {
        "slug": "lpg"
    },
    "next_hop": "198.51.100.1",
    "reverse_ptr": "192.0.2.123.cust.cloudscale.ch",
    "tags": {}
}

@responses.activate
def test_floating_ip_get_all():
    network_id = "192.0.2.123"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips',
        json=[FLOATING_IP_RESP],
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips',
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a',
        'token',
        'floating-ip',
        'list',
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a',
        'token',
        'floating-ip',
        'list',
    ])
    assert result.exit_code > 0

@responses.activate
def test_floating_ip_get_by_uuid():
    network_id = "192.0.2.123"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips/' + network_id,
        json=FLOATING_IP_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips/' + network_id,
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'floating-ip',
        'show',
        network_id,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'floating-ip',
        'show',
        network_id,
    ])
    assert result.exit_code > 0

@responses.activate
def test_floating_ip_delete():
    network_id = "192.0.2.123"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips/' + network_id,
        json=FLOATING_IP_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips/unknown',
        json=FLOATING_IP_RESP,
        status=200)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips/' + network_id,
        status=204)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips/unknown',
        json={
            "detail": "Not found."
        },
        status=404)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'floating-ip',
        'delete',
        network_id,
    ])
    assert result.exit_code == 1
    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'floating-ip',
        'delete',
        network_id,
        '--force',
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'floating-ip',
        'delete',
        '--force',
        'unknown',
    ])
    assert result.exit_code > 0

@responses.activate
def test_floating_ip_create():
    ip_version = 4
    server_uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips',
        json=FLOATING_IP_RESP,
        status=201)
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips',
        json=FLOATING_IP_RESP,
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'floating-ip',
        'create',
        '--ip-version',
        ip_version,
        '--server-uuid',
        server_uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'floating-ip',
        'create',
        '--ip-version',
        ip_version,
        '--server-uuid',
        server_uuid,
    ])
    assert result.exit_code > 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'floating-ip',
        'create',
        '--ip-version',
        6,
        '--server-uuid',
        server_uuid,
    ])
    assert result.exit_code > 0


@responses.activate
def test_floating_ip_update():
    network_id = "192.0.2.123"
    reverse_ptr = "192.0.2.123.cust.cloudscale.ch"
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips/' + network_id,
        json=FLOATING_IP_RESP,
        status=204)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips/' + network_id,
        json=FLOATING_IP_RESP,
        status=200)
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/floating-ips/' + network_id,
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'floating-ip',
        'update',
        '--reverse-ptr',
        reverse_ptr,
        network_id,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'floating-ip',
        'update',
        '--reverse-ptr',
        reverse_ptr,
        network_id,
    ])
    assert result.exit_code > 0


def test_floating_ip_missing_api_key():
    runner = CliRunner()
    result = runner.invoke(cli, [
        'floating-ip',
        'list',
    ])
    assert result.exit_code == 1
