import pytest

from cloudscale_cli.tags import merge_tags, tags_to_dict


@pytest.mark.parametrize(
    "tags, expected",
    [
        (None, None),
        ((), None),
        (("project=apollo",), {"project": "apollo"}),
        (("a=1", "b=2"), {"a": "1", "b": "2"}),
        (("url=https://example.com/a=b",), {"url": "https://example.com/a=b"}),
        (("empty=",), {"empty": ""}),
    ],
)
def test_tags_to_dict(tags, expected):
    assert tags_to_dict(tags) == expected


def test_tags_to_dict_without_value():
    with pytest.raises(ValueError, match="Invalid tag 'project'"):
        tags_to_dict(("project",))


@pytest.mark.parametrize(
    "current, add, clear, expected",
    [
        ({}, (), (), {}),
        ({"a": "1"}, (), (), {"a": "1"}),
        ({"a": "1"}, ("b=2",), (), {"a": "1", "b": "2"}),
        ({"a": "1"}, ("a=2",), (), {"a": "2"}),
        ({"a": "1", "b": "2"}, (), ("b",), {"a": "1"}),
        ({"a": "1"}, (), ("unknown",), {"a": "1"}),
        ({"a": "1", "b": "2"}, ("c=3",), ("a",), {"b": "2", "c": "3"}),
    ],
)
def test_merge_tags(current, add, clear, expected):
    assert merge_tags(current, add=add, clear=clear) == expected


def test_merge_tags_keeps_current_untouched():
    current = {"a": "1"}
    assert merge_tags(current, add=("b=2",)) == {"a": "1", "b": "2"}
    assert current == {"a": "1"}
