# cloudscale.ch CLI

The official [cloudscale.ch](https://www.cloudscale.ch) command line interface (CLI) client.

## Install

Packages are published on [PyPi](https://pypi.org/project/cloudscale-cli/).

Install using `pip` or alternatively [pipx](https://pipxproject.github.io/pipx/):

~~~shell
pipx install cloudscale-cli
cloudscale --version
~~~

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
  -v, --verbose              Verbose output.
  -h, --help                 Show this message and exit.

Commands:
  custom-image
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
