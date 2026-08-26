# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Minor changes

- Python 3.10 is now the minimum supported version, tested up to Python 3.14.
- cloudscale-sdk updated to 0.7.0.
- Packaging moved from `setup.py` to `pyproject.toml`, the development
  workflow uses `uv` and `ruff`.
- `--help` no longer requires an API token to be configured.

### Bug fixes

- Fixed `cloudscale server-group` not being available with Click 8.2 and newer,
  where it was registered as `cloudscale server` and shadowed the server
  commands.
- Fixed autocompletion instructions, which still used the Click 7 syntax.
- Fixed wrong column headers in table output when the listed resources did not
  all provide the same fields.

### Other changes

- Running `cloudscale` without a command still shows the help, but exits with
  the usage error code 2 as any other Click based CLI does.

## v1.5.0 (2025-06-24)

### Minor changes

- Add qcow2 as supported image import format.
- Drop support for Python <3.9.

### Bug fixes

- Fix some commands not showing up in certain configurations.

## v1.4.0 (2021-05-03)

### Minor changes

- Implemented interface support.

## v1.3.1 (2020-12-13)

### Bug fixes

- cloudscale-sdk updated to 0.6.2, fixes an issue in custom image update.

## v1.3.0 (2020-12-13)

### Minor changes

- Implemented custom image support.
- cloudscale-sdk updated to 0.6.1.

## v1.2.1 (2020-11-25)

### Bug fixes

- Fixed missing size output in volume table listing.

## v1.2.0 (2020-11-24)

### Minor changes

- Added option `attach` to volume.
- Added option `detach` to volume.
- Added option `assign` to floating IP to simplify assignment.
- Improved progress output.

### Bug fixes

- Fixed `floating-ip` to also identify by IP only (without CIDR).

## v1.1.0 (2020-11-14)

### Minor changes

- cloudscale-sdk updated to 0.5.0.
- Added `--detach` param to update option for volumes to detach.
- Added natural sort for table output.

## v1.0.1 (2020-10-09)

Maintenance release.

### Minor changes

- cloudscale-sdk updated to 0.4.0.

### Bug fixes

- Fixed `cloudscale server ssh` fails using UUID (https://github.com/cloudscale-ch/cloudscale-cli/issues/30).

### Other changes

- Package marked as `Stable/Production` on Pypi.

## v1.0.0 (2020-09-25)

First stable release.
