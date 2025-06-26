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

## Documentation

Please visit [https://cloudscale-ch.github.io/cloudscale-cli](https://cloudscale-ch.github.io/cloudscale-cli).

## Releases

To create a new release, follow these steps:

1. Create a branch named `release/<major>.<minor>.<patch>`.
2. Create a PR of the branch and get it approved.
3. Merge the change.
4. Tag the release commit and push the tags.

The branch should include the following:

- A single commit that updates the release.
- A version update in `cloudscale_cli/version.py`.
- An updated changelog in `CHANGELOG.md`.
