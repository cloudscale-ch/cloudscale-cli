# Authentication

## Config File with Profiles

Creating an ini file in your `$XDG_CONFIG_HOME/cloudscale/cloudscale.ini`, `.cloudscale.ini` (leading dot) in your `$HOME` or a `cloudscale.ini` (without leading dot) in the `CWD` with the following schema:

~~~ini
[default]
api_token = <token>
~~~

The default profile taken if available is `default`. The profile can be chosen by passing `--profile` or `CLOUDSCALE_PROFILE` ENV variable.

~~~shell
export CLOUDSCALE_PROFILE=staging
~~~

~~~ini
[production]
api_token = <token>

[staging]
api_token = <token>
~~~

Passing the command line option will overwrite the ENV var as one would expect:

~~~shell
cloudscale --profile production server list
~~~

## Command Line Argument

Passing the `--api-token` parameter:

~~~shell
cloudscale --api-token <your_token> server create ...
~~~

## By Evironment Variable

Using the ENV `CLOUDSCALE_API_TOKEN` variable:

~~~shell
export CLOUDSCALE_API_TOKEN=<your token>
cloudscale flavor list
~~~
