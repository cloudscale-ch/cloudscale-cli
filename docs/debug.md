# Verbosity and Debugging

Increase the verbosity by changing the log level from its default value `ERROR` to the value `INFO`:

~~~shell
cloudscale --debug server list
~~~

or alternatively

~~~shell
export CLOUDSCALE_DEBUG=1
cloudscale server list
~~~

To set the default log level e.g. to `DEBUG` use the `CLOUDSCALE_LOG_LEVEL` environment variable:

~~~shell
export CLOUDSCALE_LOG_LEVEL=debug
cloudscale server list
~~~
