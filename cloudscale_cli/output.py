"""Rendering of API responses."""

import json
from collections.abc import Sequence
from typing import Any

import jmespath
from pygments import formatters, highlight, lexers
from tabulate import tabulate

OUTPUT_FORMATS = ["table", "json"]


def transform_json(data: Any, expression: str | None = None) -> Any:
    """Reshape data by a JMESPath expression, if one is given."""
    if not expression:
        return data
    return jmespath.search(expression, data)


def to_table(data: Sequence[dict], headers: Sequence[str]) -> str:
    """Render a list of resources as a table.

    Only headers found in at least one of the resources are rendered, so
    that resources not providing a specific field do not end up with an
    empty column.
    """
    visible = [header for header in headers if any(header in d for d in data)]
    rows = [[_to_cell(d.get(header), header) for header in visible] for d in data]
    return tabulate(rows, headers=[h.upper().replace("_", " ") for h in visible])


def _to_cell(value: Any, header: str) -> Any:
    """Flatten a single API value into something printable."""
    if header == "tags" and isinstance(value, dict):
        return ", ".join(f"{key}={val}" for key, val in value.items())

    if isinstance(value, dict):
        return _label(value)

    if isinstance(value, list):
        labels = (_label(v) if isinstance(v, dict) else v for v in value)
        return ", ".join(str(label) for label in labels if label is not None)

    return value


def _label(value: dict) -> str | None:
    """Return the human readable identifier of a nested resource."""
    return value.get("name") or value.get("slug")


def to_pretty_json(data: Any) -> str:
    """Format JSON to be human readable."""
    result = json.dumps(data, sort_keys=True, indent=4)
    return highlight(result, lexers.JsonLexer(), formatters.TerminalFormatter())
