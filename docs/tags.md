# Working with Tags

## Add/Update Tags

Add/Update tags (but keep all existing with different keys):

~~~shell
cloudscale <resource> update <uuid> --tag project=apollo --tag stage=prod
~~~

## Delete a single Tag

Delete a tag (but keep all others existing):

~~~shell
cloudscale <resource> update <uuid> --clear-tag status
~~~

## Add/Update and remove Tags at once

Add/Update tags and remove a specific tag key:

~~~shell
cloudscale <resource> update <uuid> \
--tag project=apollo --tag stage=prod --clear-tag status
~~~

Add/Update tags, remove other tags:

~~~shell
cloudscale <resource> update <uuid> \
--tag project=apollo --tag stage=prod --clear-all-tags
~~~
