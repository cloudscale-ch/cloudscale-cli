# cloudscale.ch CLI

The official [cloudscale.ch](https://www.cloudscale.ch) command line interface (CLI) client.

## Install

Packages are publish on [PyPi](https://pypi.org/project/cloudscale-cli/).

Install using `pip` or alternatively [pipx](https://pipxproject.github.io/pipx/):

~~~shell
pipx install cloudscale-cli
cloudscale --version
~~~

!!! note
    The `PATH` variable may need to be extended. You should get a hint while installing it.

## Usage

~~~shell
cloudscale --help
~~~

~~~raw
Usage: cloudscale [OPTIONS] COMMAND [ARGS]...

Options:
  --version                  Show the version and exit.
  -a, --api-token TEXT       API token.
  -p, --profile TEXT         Profile used in config file.
  --debug                    Enables debug log output.
  -o, --output [table|json]  Output format.  [default: table]
  -h, --help                 Show this message and exit.

Commands:
  flavor
  floating-ip
  image
  network
  objects-user
  region
  server
  server-group
  subnet
  volume
~~~
