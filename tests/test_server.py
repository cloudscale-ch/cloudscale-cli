import json

import pytest
import responses
from click.testing import CliRunner
from cloudscale import CLOUDSCALE_API_URL

from cloudscale_cli.cli import cli

SERVER_RESP = {
    "uuid": "47cec963-fcd2-482f-bdb6-24461b2d47b1",
    "name": "db-master",
    "status": "running",
    "zone": {"slug": "lpg1"},
    "flavor": {
        "slug": "flex-4",
    },
    "image": {
        "slug": "debian-9",
    },
    "server_groups": [],
    "anti_affinity_with": [],
    "tags": {"project": "gemini"},
}


@responses.activate
def test_server_get_all():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/servers",
        json=[SERVER_RESP],
        status=200,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/servers",
        json={"detail": "Server error."},
        status=500,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "list",
        ],
    )
    assert result.exit_code == 0
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "list",
        ],
    )
    assert result.exit_code > 0


@responses.activate
def test_server_get_all_fitlered():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/servers",
        json=[SERVER_RESP],
        status=200,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli, ["-a", "token", "server", "list", "--filter-tag", "project=gemini"]
    )
    assert result.exit_code == 0
    result = runner.invoke(
        cli, ["-a", "token", "server", "list", "--filter-tag", "project"]
    )
    assert result.exit_code == 0


@responses.activate
def test_server_get_by_uuid():
    uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/servers/" + uuid,
        json=SERVER_RESP,
        status=200,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/servers/" + uuid,
        json={"detail": "Server error."},
        status=500,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "show",
            uuid,
        ],
    )
    assert result.exit_code == 0
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "show",
            uuid,
        ],
    )
    assert result.exit_code > 0


@responses.activate
def test_server_delete():
    uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/servers/" + uuid,
        json=SERVER_RESP,
        status=200,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/servers/unknown",
        json=SERVER_RESP,
        status=200,
    )
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_URL + "/servers/" + uuid,
        status=204,
    )
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_URL + "/servers/unknown",
        json={"detail": "Not found."},
        status=404,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "delete",
            uuid,
        ],
    )
    assert result.exit_code == 1
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "delete",
            "--force",
            uuid,
        ],
    )
    assert result.exit_code == 0
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "delete",
            "--force",
            "unknown",
        ],
    )
    assert result.exit_code > 0


def test_server_missing_api_key():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "server",
            "list",
        ],
    )
    assert result.exit_code == 1


@responses.activate
def test_server_create():
    name = "db-master"
    flavor = "flex-4"
    image = "debian9"

    responses.add(
        responses.POST,
        CLOUDSCALE_API_URL + "/servers",
        json=SERVER_RESP,
        status=201,
    )
    responses.add(
        responses.POST,
        CLOUDSCALE_API_URL + "/servers",
        json={"detail": "Server error."},
        status=500,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "create",
            "--name",
            name,
            "--flavor",
            flavor,
            "--image",
            image,
        ],
    )
    assert result.exit_code == 0
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "create",
            "--name",
            name,
            "--flavor",
            flavor,
            "--image",
            image,
        ],
    )
    assert result.exit_code > 0


@responses.activate
def test_server_update():
    uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    name = "db-master"
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_URL + "/servers/" + uuid,
        status=204,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/servers/" + uuid,
        json=SERVER_RESP,
        status=200,
    )
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_URL + "/servers/" + uuid,
        json={"detail": "Server error."},
        status=500,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "update",
            "--name",
            name,
            "--tag",
            "project=gemini",
            uuid,
        ],
    )
    assert result.exit_code == 0
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "update",
            "--name",
            name,
            "--tag",
            "project=gemini",
            uuid,
        ],
    )
    assert result.exit_code > 0


@responses.activate
def test_server_start():
    uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    responses.add(
        responses.POST,
        CLOUDSCALE_API_URL + "/servers/" + uuid + "/start",
        status=204,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/servers/" + uuid,
        json=SERVER_RESP,
        status=200,
    )
    responses.add(
        responses.POST,
        CLOUDSCALE_API_URL + "/servers/" + uuid + "/start",
        json={"detail": "Server error."},
        status=500,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "start",
            uuid,
        ],
    )
    assert result.exit_code == 0
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "start",
            uuid,
        ],
    )
    assert result.exit_code > 0


@responses.activate
def test_server_stop():
    uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    responses.add(
        responses.POST,
        CLOUDSCALE_API_URL + "/servers/" + uuid + "/stop",
        status=204,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/servers/" + uuid,
        json=SERVER_RESP,
        status=200,
    )
    responses.add(
        responses.POST,
        CLOUDSCALE_API_URL + "/servers/" + uuid + "/stop",
        json={"detail": "Server error."},
        status=500,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "stop",
            uuid,
        ],
    )
    assert result.exit_code == 0
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "stop",
            uuid,
        ],
    )
    assert result.exit_code > 0


@responses.activate
def test_server_reboot():
    uuid = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
    responses.add(
        responses.POST,
        CLOUDSCALE_API_URL + "/servers/" + uuid + "/reboot",
        status=204,
    )
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + "/servers/" + uuid,
        json=SERVER_RESP,
        status=200,
    )
    responses.add(
        responses.POST,
        CLOUDSCALE_API_URL + "/servers/" + uuid + "/reboot",
        json={"detail": "Server error."},
        status=500,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "reboot",
            uuid,
        ],
    )
    assert result.exit_code == 0
    result = runner.invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "reboot",
            uuid,
        ],
    )
    assert result.exit_code > 0


SERVER_SSH_RESP = {
    **SERVER_RESP,
    "href": CLOUDSCALE_API_URL + "/servers/47cec963-fcd2-482f-bdb6-24461b2d47b1",
    "image": {"slug": "debian-12", "default_username": "debian"},
    "interfaces": [
        {"type": "public", "addresses": [{"address": "192.0.2.1"}]},
        {"type": "private", "addresses": [{"address": "10.0.0.1"}]},
    ],
}


@pytest.fixture
def ssh_calls(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "cloudscale_cli.commands.server.os.system", lambda cmd: calls.append(cmd)
    )
    return calls


@responses.activate
def test_server_ssh(ssh_calls):
    uuid = SERVER_RESP["uuid"]
    responses.get(CLOUDSCALE_API_URL + "/servers/" + uuid, json=SERVER_SSH_RESP)

    result = CliRunner().invoke(cli, ["-a", "token", "server", "ssh", uuid])
    assert result.exit_code == 0
    assert ssh_calls == ["ssh debian@192.0.2.1"]


@responses.activate
def test_server_ssh_private_interface(ssh_calls):
    uuid = SERVER_RESP["uuid"]
    responses.get(CLOUDSCALE_API_URL + "/servers/" + uuid, json=SERVER_SSH_RESP)

    result = CliRunner().invoke(
        cli, ["-a", "token", "server", "ssh", uuid, "--interface", "private"]
    )
    assert result.exit_code == 0
    assert ssh_calls == ["ssh debian@10.0.0.1"]


@responses.activate
def test_server_ssh_by_name(ssh_calls):
    responses.get(
        CLOUDSCALE_API_URL + "/servers/db-master",
        json={"detail": "Not found."},
        status=404,
    )
    responses.get(CLOUDSCALE_API_URL + "/servers", json=[SERVER_SSH_RESP])

    result = CliRunner().invoke(cli, ["-a", "token", "server", "ssh", "db-master"])
    assert result.exit_code == 0
    assert ssh_calls == ["ssh debian@192.0.2.1"]


@responses.activate
def test_server_ssh_without_interface(ssh_calls):
    uuid = SERVER_RESP["uuid"]
    responses.get(
        CLOUDSCALE_API_URL + "/servers/" + uuid,
        json={**SERVER_SSH_RESP, "interfaces": []},
    )

    result = CliRunner().invoke(cli, ["-a", "token", "server", "ssh", uuid])
    assert result.exit_code == 1
    assert "No IP on interface found: public" in result.output
    assert ssh_calls == []


@responses.activate
def test_server_ssh_not_found(ssh_calls):
    responses.get(
        CLOUDSCALE_API_URL + "/servers/nope", json={"detail": "Not found."}, status=404
    )
    responses.get(CLOUDSCALE_API_URL + "/servers", json=[], status=500)

    result = CliRunner().invoke(cli, ["-a", "token", "server", "ssh", "nope"])
    assert result.exit_code == 1
    assert ssh_calls == []


@responses.activate
def test_server_create_with_interfaces():
    create = responses.post(CLOUDSCALE_API_URL + "/servers", json=SERVER_RESP)

    result = CliRunner().invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "create",
            "--name",
            "db-master",
            "--flavor",
            "flex-4",
            "--image",
            "debian-12",
            "--interface",
            "network=public",
            "--interface",
            "subnet=8e79cc58-dc9f-4f68-aeae-e0eac3f06f16",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(create.calls[0].request.body)
    assert payload["interfaces"] == [
        {"network": "public"},
        {"addresses": [{"subnet": "8e79cc58-dc9f-4f68-aeae-e0eac3f06f16"}]},
    ]
    assert "use_public_network" not in payload


@responses.activate
def test_server_create_with_invalid_interface():
    result = CliRunner().invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "create",
            "--name",
            "db-master",
            "--flavor",
            "flex-4",
            "--image",
            "debian-12",
            "--interface",
            "foo",
        ],
    )
    assert result.exit_code == 1
    assert "Cannot add an interface without network or subnet definition" in (
        result.output
    )


@responses.activate
def test_server_update_with_invalid_interface():
    uuid = SERVER_RESP["uuid"]
    responses.get(CLOUDSCALE_API_URL + "/servers/" + uuid, json=SERVER_RESP)

    result = CliRunner().invoke(
        cli, ["-a", "token", "server", "update", uuid, "--interface", "foo"]
    )
    assert result.exit_code == 1


@responses.activate
def test_server_create_with_unknown_name_format():
    result = CliRunner().invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "create",
            "--name",
            "db-{unknown}",
            "--flavor",
            "flex-4",
            "--image",
            "debian-12",
        ],
    )
    assert result.exit_code == 1
    assert "Could not format name" in result.output


@responses.activate
def test_server_create_multiple_with_wait():
    uuid = SERVER_RESP["uuid"]
    responses.post(
        CLOUDSCALE_API_URL + "/servers", json={**SERVER_RESP, "status": "changing"}
    )
    responses.get(
        CLOUDSCALE_API_URL + "/servers/" + uuid,
        json={**SERVER_RESP, "status": "running"},
    )

    result = CliRunner().invoke(
        cli,
        [
            "-a",
            "token",
            "server",
            "create",
            "--name",
            "db-{counter}-{uid}",
            "--flavor",
            "flex-4",
            "--image",
            "debian-12",
            "--count",
            "2",
            "--wait",
        ],
    )
    assert result.exit_code == 0
    assert len(responses.calls) == 4
