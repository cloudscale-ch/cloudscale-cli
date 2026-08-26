from cloudscale_cli.spinner import DummySpinner


def test_dummy_spinner_can_be_used_as_context_manager():
    with DummySpinner(text="Querying") as spinner:
        spinner.text = "Still querying"
    assert spinner.text == "Still querying"


def test_dummy_spinner_writes_to_stdout(capsys):
    DummySpinner().write("hello")
    assert capsys.readouterr().out == "hello\n"


def test_dummy_spinner_swallows_any_call():
    spinner = DummySpinner()
    spinner.ok("done")
    spinner.whatever.nested()
