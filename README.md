![license](https://img.shields.io/pypi/l/cloudscale-cli.svg)
![python versions](https://img.shields.io/pypi/pyversions/cloudscale-cli.svg)
![status](https://img.shields.io/pypi/status/cloudscale-cli.svg)
[![pypi version](https://img.shields.io/pypi/v/cloudscale-cli.svg)](https://pypi.org/project/cloudscale-cli/)
![PyPI - Downloads](https://img.shields.io/pypi/dw/cloudscale-cli)

# cloudscale.ch CLI

The official [cloudscale.ch](https://www.cloudscale.ch) command line interface (CLI) client.

## Install

~~~shell
pipx install cloudscale-cli
cloudscale --help
~~~

## Usage

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

## Documentation

Please visit [https://cloudscale-ch.github.io/cloudscale-cli](https://cloudscale-ch.github.io/cloudscale-cli).
