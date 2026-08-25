"""Handling of resource tags passed on the command line."""

from collections.abc import Iterable


def tags_to_dict(tags: Iterable[str] | None) -> dict[str, str] | None:
    """Turn a sequence of ``key=value`` strings into a dict.

    Returns ``None`` if no tags were given, so the API is not asked to
    change tags at all.

    Raises:
        ValueError: A tag is not in the ``key=value`` format.
    """
    if not tags:
        return None

    result = {}
    for tag in tags:
        if "=" not in tag:
            raise ValueError(f"Invalid tag '{tag}'. Use the format 'name=value'.")
        key, value = tag.split("=", maxsplit=1)
        result[key] = value
    return result


def merge_tags(
    current: dict[str, str],
    add: Iterable[str] = (),
    clear: Iterable[str] = (),
) -> dict[str, str]:
    """Return the tags of a resource with tags removed and added.

    Args:
        current: Tags currently assigned to the resource.
        add: Tags to add or update in ``key=value`` format.
        clear: Tag keys to remove.

    Raises:
        ValueError: A tag to add is not in the ``key=value`` format.
    """
    tags = dict(current)
    for key in clear:
        tags.pop(key, None)
    tags.update(tags_to_dict(add) or {})
    return tags
