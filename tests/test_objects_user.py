from cloudscale import CLOUDSCALE_API_ENDPOINT
from cloudscale_cli.cli import cli
import responses
import click
from click.testing import CliRunner

OBJECTS_USER_RESP = {
    "href": "https://api.cloudscale.ch/v1/objects-users/6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15",
    "id": "6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15",
    "display_name": "alan",
    "keys": [
        {
            "access_key": "0ZTAIBKSGYBRHQ09G11W",
            "secret_key": "bn2ufcwbIa0ARLc5CLRSlVaCfFxPHOpHmjKiH34T"
        }
    ],
    "tags": {
        "project": "apollo"
    }
}

@responses.activate
def test_objects_user_get_all():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/objects-users',
        json=[OBJECTS_USER_RESP],
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/objects-users?tag:project=apollo',
        json=[OBJECTS_USER_RESP],
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/objects-users',
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a',
        'token',
        'objects-user',
        'list',
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a',
        'token',
        'objects-user',
        'list',
        '--filter-tag',
        'project=apollo',
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a',
        'token',
        'objects-user',
        'list',
    ])
    assert result.exit_code > 0

@responses.activate
def test_objects_user_get_by_uuid():
    uuid = "6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/objects-users/' + uuid,
        json=OBJECTS_USER_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/objects-users/unknown',
        json={},
        status=404)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'objects-user',
        'show',
        uuid,
    ])
    assert result.exit_code == 0

    result = runner.invoke(cli, [
        '-a', 'token',
        'objects-user',
        'show',
        'unknown',
    ])
    assert result.exit_code > 0

@responses.activate
def test_objects_user_delete():
    uuid = "6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/objects-users/' + uuid,
        json=OBJECTS_USER_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/objects-users/unknown',
        json=OBJECTS_USER_RESP,
        status=200)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_ENDPOINT + '/objects-users/' + uuid,
        status=204)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_ENDPOINT + '/objects-users/unknown',
        json={},
        status=404)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'objects-user',
        'delete',
        uuid,
    ])
    assert result.exit_code == 1
    result = runner.invoke(cli, [
        '-a', 'token',
        'objects-user',
        'delete',
        '--force',
        uuid,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'objects-user',
        'delete',
        '--force',
        'unknown',
    ])
    assert result.exit_code > 0

@responses.activate
def test_objects_user_create():
    display_name = "alan"

    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/objects-users',
        json=OBJECTS_USER_RESP,
        status=201)
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/objects-users',
        json={},
        status=500)
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/objects-users',
        json=OBJECTS_USER_RESP,
        status=201)
    responses.add(
        responses.POST,
        CLOUDSCALE_API_ENDPOINT + '/objects-users',
        json={},
        status=500)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'objects-user',
        'create',
        '--display-name',
        display_name,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'objects-user',
        'create',
        '--display-name',
        display_name,
    ])
    assert result.exit_code > 0

@responses.activate
def test_objects_user_update():
    uuid = "6fe39134bf4178747eebc429f82cfafdd08891d4279d0d899bc4012db1db6a15"
    display_name = "alan"
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/objects-users/' + uuid,
        json=OBJECTS_USER_RESP,
        status=204)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_ENDPOINT + '/objects-users/' + uuid,
        json=OBJECTS_USER_RESP,
        status=200)
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_ENDPOINT + '/objects-users/unknown',
        json={},
        status=404)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'objects-user',
        'update',
        uuid,
        '--display-name',
        display_name,
    ])
    assert result.exit_code == 0
    result = runner.invoke(cli, [
        '-a', 'token',
        'objects-user',
        'update',
        'unknown',
        '--display-name',
        display_name,
    ])
    assert result.exit_code > 0

def test_objects_user_missing_api_key():
    runner = CliRunner()
    result = runner.invoke(cli, [
        'objects-user',
        'list',
    ])
    assert result.exit_code == 1
