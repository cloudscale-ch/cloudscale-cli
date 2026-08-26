"""Tests of the commands shared by all resources, run against servers."""

import json
import re

import responses
from click.testing import CliRunner
from cloudscale import CLOUDSCALE_API_URL

from cloudscale_cli.cli import cli

SERVERS_URL = CLOUDSCALE_API_URL + "/servers"
UUID = "47cec963-fcd2-482f-bdb6-24461b2d47b1"
OTHER_UUID = "11111111-fcd2-482f-bdb6-24461b2d47b1"


def server_resp(uuid=UUID, name="db-master", status="running"):
    return {
        "href": f"{SERVERS_URL}/{uuid}",
        "uuid": uuid,
        "name": name,
        "status": status,
        "zone": {"slug": "lpg1"},
        "flavor": {"slug": "flex-4"},
        "image": {"slug": "debian-12"},
        "server_groups": [],
        "volumes": [],
        "interfaces": [
            {"type": "public", "addresses": [{"address": "192.0.2.1"}]},
        ],
        "tags": {"project": "gemini"},
    }


def run(*args):
    return CliRunner().invoke(cli, ["-a", "token", *args])


def strip_colors(output):
    return re.sub(r"\x1b\[[0-9;]*m", "", output)


@responses.activate
def test_json_output():
    responses.get(SERVERS_URL, json=[server_resp()])

    result = run("-o", "json", "server", "list")
    assert result.exit_code == 0
    assert json.loads(strip_colors(result.output)) == [server_resp()]


@responses.activate
def test_json_output_of_a_single_resource():
    responses.get(f"{SERVERS_URL}/{UUID}", json=server_resp())

    result = run("-o", "json", "server", "show", UUID)
    assert result.exit_code == 0
    assert json.loads(strip_colors(result.output)) == server_resp()


@responses.activate
def test_verbose_output_shows_more_headers():
    responses.get(SERVERS_URL, json=[server_resp()])
    assert "PUBLIC IPS" not in run("server", "list").output

    responses.get(SERVERS_URL, json=[server_resp()])
    assert "PUBLIC IPS" in run("-v", "server", "list").output


@responses.activate
def test_table_is_sorted_naturally():
    responses.get(
        SERVERS_URL,
        json=[
            server_resp(name="server-10"),
            server_resp(name="Server-2"),
            server_resp(name="server-1"),
        ],
    )

    result = run("server", "list")
    assert result.exit_code == 0
    names = [line.split()[0] for line in result.output.splitlines()[2:]]
    assert names == ["server-1", "Server-2", "server-10"]


@responses.activate
def test_show_by_name():
    responses.get(f"{SERVERS_URL}/db-master", json={"detail": "Not found."}, status=404)
    responses.get(SERVERS_URL, json=[server_resp()])

    result = run("server", "show", "db-master")
    assert result.exit_code == 0
    assert "db-master" in result.output


@responses.activate
def test_show_by_name_not_found():
    responses.get(f"{SERVERS_URL}/nope", json={"detail": "Not found."}, status=404)
    responses.get(SERVERS_URL, json=[server_resp()])

    result = run("server", "show", "nope")
    assert result.exit_code == 1
    assert "No resource found for server having UUID or name: nope" in result.output


@responses.activate
def test_show_by_ambiguous_name():
    responses.get(f"{SERVERS_URL}/db-master", json={"detail": "Not found."}, status=404)
    responses.get(
        SERVERS_URL,
        json=[server_resp(), server_resp(uuid=OTHER_UUID)],
    )

    # Showing all matches is fine, ...
    result = run("server", "show", "db-master")
    assert result.exit_code == 0
    assert result.output.count("db-master") == 2


@responses.activate
def test_update_by_ambiguous_name():
    responses.get(f"{SERVERS_URL}/db-master", json={"detail": "Not found."}, status=404)
    responses.get(SERVERS_URL, json=[server_resp(), server_resp(uuid=OTHER_UUID)])

    # ... but a single resource is required to change one.
    result = run("server", "update", "db-master", "--name", "new")
    assert result.exit_code == 1
    assert "More than one resource found" in result.output


@responses.activate
def test_update_by_name_resolves_the_uuid():
    responses.get(f"{SERVERS_URL}/db-master", json={"detail": "Not found."}, status=404)
    responses.get(SERVERS_URL, json=[server_resp()])
    patch = responses.patch(f"{SERVERS_URL}/{UUID}", status=204)
    responses.get(f"{SERVERS_URL}/{UUID}", json=server_resp(name="new"))

    result = run("server", "update", "db-master", "--name", "new")
    assert result.exit_code == 0
    assert patch.call_count == 1


@responses.activate
def test_update_tags_are_merged():
    responses.get(f"{SERVERS_URL}/{UUID}", json=server_resp())
    patch = responses.patch(f"{SERVERS_URL}/{UUID}", status=204)

    result = run(
        "server",
        "update",
        UUID,
        "--tag",
        "stage=prod",
        "--clear-tag",
        "project",
    )
    assert result.exit_code == 0
    assert json.loads(patch.calls[0].request.body)["tags"] == {"stage": "prod"}


@responses.activate
def test_update_clear_all_tags():
    responses.get(f"{SERVERS_URL}/{UUID}", json=server_resp())
    patch = responses.patch(f"{SERVERS_URL}/{UUID}", status=204)

    result = run("server", "update", UUID, "--clear-all-tags")
    assert result.exit_code == 0
    assert json.loads(patch.calls[0].request.body)["tags"] == {}


@responses.activate
def test_update_without_tags_keeps_them():
    responses.get(f"{SERVERS_URL}/{UUID}", json=server_resp())
    patch = responses.patch(f"{SERVERS_URL}/{UUID}", status=204)

    result = run("server", "update", UUID, "--name", "new")
    assert result.exit_code == 0
    assert "tags" not in json.loads(patch.calls[0].request.body)


@responses.activate
def test_list_with_filter_json():
    responses.get(
        SERVERS_URL,
        json=[server_resp(), server_resp(uuid=OTHER_UUID, status="stopped")],
    )

    result = run("server", "list", "--filter-json", "[?status == `stopped`]")
    assert result.exit_code == 0
    assert result.output.count("stopped") == 1


@responses.activate
def test_list_with_invalid_filter_json():
    responses.get(SERVERS_URL, json=[server_resp()])

    result = run("server", "list", "--filter-json", "[?status ==")
    assert result.exit_code == 1
    assert "filter_json error" in result.output


@responses.activate
def test_list_without_results():
    responses.get(SERVERS_URL, json=[])

    result = run("server", "list")
    assert result.exit_code == 0
    assert result.output == ""


def test_list_with_action_and_delete():
    result = run("server", "list", "--action", "start", "--delete")
    assert result.exit_code == 1
    assert "mutually exclusive" in result.output


@responses.activate
def test_list_delete_all():
    responses.get(SERVERS_URL, json=[server_resp(), server_resp(uuid=OTHER_UUID)])
    first = responses.delete(f"{SERVERS_URL}/{UUID}", status=204)
    second = responses.delete(f"{SERVERS_URL}/{OTHER_UUID}", status=204)

    result = run("server", "list", "--delete", "--force")
    assert result.exit_code == 0
    assert first.call_count == 1
    assert second.call_count == 1


@responses.activate
def test_list_delete_all_needs_confirmation():
    responses.get(SERVERS_URL, json=[server_resp()])
    delete = responses.delete(f"{SERVERS_URL}/{UUID}", status=204)

    result = CliRunner().invoke(
        cli, ["-a", "token", "server", "list", "--delete"], input="n\n"
    )
    assert result.exit_code == 1
    assert delete.call_count == 0


@responses.activate
def test_list_delete_all_without_href():
    responses.get(SERVERS_URL, json=[{"uuid": UUID, "name": "db-master"}])

    result = run("server", "list", "--delete", "--force")
    assert result.exit_code == 1
    assert "No href found, could not delete." in result.output


@responses.activate
def test_list_action_on_all():
    responses.get(SERVERS_URL, json=[server_resp(status="stopped")])
    start = responses.post(f"{SERVERS_URL}/{UUID}/start", status=204)

    result = run("server", "list", "--action", "start", "--force")
    assert result.exit_code == 0
    assert start.call_count == 1


@responses.activate
def test_list_action_on_all_with_wait():
    responses.get(SERVERS_URL, json=[server_resp(status="changing")])
    start = responses.post(f"{SERVERS_URL}/{UUID}/start", status=204)
    responses.get(f"{SERVERS_URL}/{UUID}", json=server_resp(status="running"))

    result = run("server", "list", "--action", "start", "--force", "--wait")
    assert result.exit_code == 0
    assert start.call_count == 1


@responses.activate
def test_action_with_wait():
    responses.get(f"{SERVERS_URL}/{UUID}", json=server_resp(status="changing"))
    responses.post(f"{SERVERS_URL}/{UUID}/start", status=204)
    responses.get(f"{SERVERS_URL}/{UUID}", json=server_resp(status="running"))

    result = run("server", "start", UUID, "--wait")
    assert result.exit_code == 0
    assert "running" in result.output


@responses.activate
def test_invalid_tag_on_create():
    result = run(
        "server",
        "create",
        "--name",
        "a",
        "--flavor",
        "f",
        "--image",
        "i",
        "--tag",
        "project",
    )
    assert result.exit_code == 1
    assert "Invalid tag 'project'" in result.output


@responses.activate
def test_invalid_tag_on_update():
    responses.get(f"{SERVERS_URL}/{UUID}", json=server_resp())

    result = run("server", "update", UUID, "--tag", "project")
    assert result.exit_code == 1
    assert "Invalid tag 'project'" in result.output


def test_missing_api_token():
    result = CliRunner().invoke(cli, ["server", "list"])
    assert result.exit_code == 1
    assert "Missing API key" in result.output


def test_unknown_profile():
    result = CliRunner().invoke(cli, ["-p", "nope", "server", "list"])
    assert result.exit_code == 1
    assert "Profile 'nope' not found" in result.output


def test_help_needs_no_api_token():
    assert CliRunner().invoke(cli, ["server", "list", "--help"]).exit_code == 0


@responses.activate
def test_list_action_needs_confirmation():
    responses.get(SERVERS_URL, json=[server_resp(status="stopped")])
    start = responses.post(f"{SERVERS_URL}/{UUID}/start", status=204)

    result = CliRunner().invoke(
        cli, ["-a", "token", "server", "list", "--action", "start"], input="n\n"
    )
    assert result.exit_code == 1
    assert start.call_count == 0


@responses.activate
def test_update_with_wait():
    responses.get(f"{SERVERS_URL}/{UUID}", json=server_resp(status="changing"))
    responses.patch(f"{SERVERS_URL}/{UUID}", status=204)
    responses.get(f"{SERVERS_URL}/{UUID}", json=server_resp(status="running"))

    result = run("server", "update", UUID, "--flavor", "flex-8", "--wait")
    assert result.exit_code == 0
    assert "running" in result.output


@responses.activate
def test_wait_gives_up_eventually(monkeypatch):
    monkeypatch.setattr("cloudscale_cli.command.time.sleep", lambda seconds: None)
    responses.get(f"{SERVERS_URL}/{UUID}", json=server_resp(status="changing"))
    responses.post(f"{SERVERS_URL}/{UUID}/start", status=204)

    result = run("server", "start", UUID, "--wait")
    assert result.exit_code == 0
    assert "changing" in result.output
