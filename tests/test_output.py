import json
import re

from cloudscale_cli.output import to_pretty_json, to_table, transform_json


def test_transform_json_without_expression():
    data = [{"name": "a"}]
    assert transform_json(data) is data


def test_transform_json():
    data = [{"name": "a", "zone": {"slug": "lpg1"}}]
    assert transform_json(data, "[].{name: name}") == [{"name": "a"}]


def test_to_table_headers_are_upper_case():
    table = to_table([{"size_gb": 10}], ["size_gb"])
    assert table.splitlines()[0].strip() == "SIZE GB"


def test_to_table_skips_headers_not_in_data():
    table = to_table([{"name": "a"}], ["name", "flavor"])
    assert "FLAVOR" not in table


def test_to_table_renders_all_rows():
    table = to_table([{"name": "a"}, {"name": "b"}], ["name"])
    assert [line.strip() for line in table.splitlines()] == ["NAME", "------", "a", "b"]


def test_to_table_with_rows_of_different_fields():
    table = to_table([{"name": "a"}, {"name": "b", "slug": "s"}], ["name", "slug"])
    assert table.splitlines()[0].split() == ["NAME", "SLUG"]
    assert table.splitlines()[-1].split() == ["b", "s"]


def test_to_table_flattens_tags():
    table = to_table([{"tags": {"a": "1", "b": "2"}}], ["tags"])
    assert "a=1, b=2" in table


def test_to_table_flattens_nested_resource():
    table = to_table([{"zone": {"slug": "lpg1"}}], ["zone"])
    assert "lpg1" in table


def test_to_table_prefers_name_of_nested_resource():
    table = to_table([{"image": {"slug": "debian-12", "name": "Debian 12"}}], ["image"])
    assert "Debian 12" in table


def test_to_table_flattens_lists():
    data = [{"zones": [{"slug": "lpg1"}, {"slug": "rma1"}], "ips": ["10.0.0.1"]}]
    table = to_table(data, ["zones", "ips"])
    assert "lpg1, rma1" in table
    assert "10.0.0.1" in table


def test_to_table_ignores_unnamed_nested_resources():
    table = to_table([{"volumes": [{"uuid": "u"}]}], ["volumes"])
    assert "u" not in table


def test_to_table_without_data():
    assert to_table([], ["name"]) == ""


def test_to_pretty_json_is_valid_json():
    result = to_pretty_json({"b": 1, "a": 2})
    # The output is syntax highlighted, strip the escape sequences again.
    plain = re.sub(r"\x1b\[[0-9;]*m", "", result)
    assert json.loads(plain) == {"a": 2, "b": 1}
    assert plain.index('"a"') < plain.index('"b"')
