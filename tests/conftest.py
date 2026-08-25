import pytest


@pytest.fixture(autouse=True)
def isolated_config(monkeypatch, tmp_path):
    """Keep the tests from picking up the config of the user running them."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("CLOUDSCALE_CONFIG", "test-cloudscale.ini")
    for name in (
        "CLOUDSCALE_API_TOKEN",
        "CLOUDSCALE_PROFILE",
        "CLOUDSCALE_DEBUG",
        "CLOUDSCALE_OUTPUT",
        "CLOUDSCALE_VERBOSE",
    ):
        monkeypatch.delenv(name, raising=False)
