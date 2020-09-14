# Authentication

There are 3 ways to configure the authentication:

- Using a config file
- Using the `--api-token` parameter
- Using the environment variable `CLOUDSCALE_API_TOKEN`

## Config File with Profiles

Create an ini file in your `$XDG_CONFIG_HOME/cloudscale/cloudscale.ini`, `.cloudscale.ini` (leading dot) in your `$HOME` or a `cloudscale.ini` (without leading dot) in the `CWD` with the following schema:

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

Use the `--api-token` parameter:

~~~shell
cloudscale --api-token <your_token> server create ...
~~~

## By Evironment Variable

Use the ENV `CLOUDSCALE_API_TOKEN` variable:

~~~shell
export CLOUDSCALE_API_TOKEN=<your token>
cloudscale flavor list
~~~
