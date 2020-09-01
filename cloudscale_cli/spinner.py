class DummySpinner:
    def __init__(self, *args, **kwargs):
        self.text = ''

    def write(self, *args, **kwargs):
        print(*args, **kwargs)

    def __getattr__(self, name):
        return self

    def __call__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        return False
