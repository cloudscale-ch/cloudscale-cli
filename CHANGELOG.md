# Changelog

All notable changes to this project will be documented in this file.

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
