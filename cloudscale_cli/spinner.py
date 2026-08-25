"""Progress spinner used while the API is queried.

Spinners only make sense on an interactive terminal. Whenever the output is
piped or redirected, a drop-in replacement is used which does not emit any
control characters.
"""

import sys


class DummySpinner:
    """A spinner that does nothing but stay out of the way."""

    def __init__(self, *args, **kwargs):
        self.text = ""

    def write(self, *args, **kwargs):
        print(*args, **kwargs)

    def __getattr__(self, name):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        return False


if sys.stdout.isatty():  # pragma: no cover
    from yaspin import yaspin as Spinner
else:
    Spinner = DummySpinner
