# Server Usage Examples

## Create Servers

Create one server:

~~~shell
cloudscale server create \
--name my-server \
--flavor flex-2 \
--image centos-7 \
--ssh-key "$(cat ~/.ssh/id_rsa.pub)"
~~~

Create up to 10 servers in a row with `--count`:

!!! tip
    When using `--count`, the option `--name` allows to use string format syntax with 2 special variables:

    - `counter`: A number representing the current interation while creating multiple servers.
    - `uid`: A random 8 char/number long string.

    This allows to create dynamic names, e.g.:

    - Single number suffix: `--name 'myserver-{counter}'`
    - Number with leading zero suffix: `--name 'server-{counter:02d}'`
    - Random string suffix: `--name 'server-{uid}'`
    - Combinations: `--name 'server-{uid}-{counter:02d}.example.com'`

~~~shell
cloudscale server create \
--name 'my-server-{uid}' \
--flavor flex-2 \
--image centos-7 \
--ssh-key "$(cat ~/.ssh/id_rsa.pub)" \
--count 10
~~~

## List Servers

Get a list as table view:

~~~shell
cloudscale server list
~~~

Get a list as JSON response:

~~~shell
cloudscale -o json server list
~~~

### Filter by Tag

List servers having the tag project with value gemini:

~~~shell
cloudscale server list --filter-tag project=gemini
~~~

List servers having a tag project:

~~~shell
cloudscale server list --filter-tag project
~~~

### Filter by JSON Query

Get a list of stopped servers:

~~~shell
cloudscale server list --filter-json '[?status == `stopped`]'
~~~

Get a list of stopped servers having tag `project=demo` and start them after accepting:

~~~shell
cloudscale server list \
--filter-tag project=demo \
--filter-json '[?status == `stopped`]' \
--action start
...
Do you want to start? [y/N]:
~~~

Start a list of stopped servers after accepting having tag `project=demo`:

~~~shell
cloudscale server list \
--filter-tag project=demo \
--filter-json '[?status == `stopped`]' \
--action start
...
Do you want to start? [y/N]:
~~~

Delete a list of stopped servers after accepting having tag `project=demo`:

~~~shell
cloudscale server list \
--filter-tag project=demo \
--filter-json '[?status == `stopped`]' \
--delete
...
Do you want to delete? [y/N]:
~~~

Get a simplified custom JSON list of stopped servers in profile `production`:

~~~shell
cloudscale \
--output json \
--profile production \
server list \
--filter-json '[?status == `stopped`].{"server_name": name, "zone": zone.slug, "image": image.slug, "flavor": flavor.slug}'
[
    {
        "flavor": "flex-8",
        "image": "rhel-7",
        "server_name": "server1",
        "zone": "rma1"
    },
    {
        "flavor": "flex-8",
        "image": "centos-7",
        "server_name": "server2",
        "zone": "rma1"
    }
]
~~~

## Server Actions

### Stop a Server

Stop a server:

~~~shell
cloudscale server stop <uuid>
~~~

### Start a Server

~~~shell
cloudscale server start <uuid>
~~~

### Delete a Server

With prompt:

~~~shell
cloudscale server delete <uuid>
~~~

Just delete without questions asked:

~~~shell
cloudscale server delete --force <uuid>
~~~
