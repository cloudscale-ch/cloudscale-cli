from cloudscale import CLOUDSCALE_API_URL
from cloudscale_cli.cli import cli
import responses
import click
from click.testing import CliRunner

CUSTOM_IMAGE_RESP = {
  "href": "https://api.cloudscale.ch/v1/custom-images/11111111-1864-4608-853a-0771b6885a3a",
  "created_at": "2020-05-29T13:18:42.511407Z",
  "uuid": "11111111-1864-4608-853a-0771b6885a3a",
  "name": "my-image",
  "slug": "my-image-slug",
  "checksums": {
    "md5": "5b3a1f21cde154cfb522b582f44f1a87",
    "sha256": "5b03bcbd00b687e08791694e47d235a487c294e58ca3b1af704120123aa3f4e6"
  },
  "user_data_handling": "pass-through",
  "zones": [
    {
      "slug": "lpg1"
    }
  ],
  "tags": {}
}

CUSTOM_IMAGE_IMPORT_RESP = {
  "href": "https://api.cloudscale.ch/v1/custom-images/import/11111111-1864-4608-853a-0771b6885a3a",
  "uuid": "11111111-1864-4608-853a-0771b6885a3a",
  "custom_image": {
      "href": "https://api.cloudscale.ch/v1/custom-images/11111111-1864-4608-853a-0771b6885a3a",
      "uuid": "11111111-1864-4608-853a-0771b6885a3a",
      "name": "my-image"
  },
  "url": "https://example.com/foo.raw",
  "status": "in_progress"
}

CUSTOM_IMAGE_IMPORT_RESP_FAILED = {
  "href": "https://api.cloudscale.ch/v1/custom-images/import/11111111-1864-4608-853a-0771b6885a3a",
  "uuid": "11111111-1864-4608-853a-0771b6885a3a",
  "custom_image": {
      "href": "https://api.cloudscale.ch/v1/custom-images/11111111-1864-4608-853a-0771b6885a3a",
      "uuid": "11111111-1864-4608-853a-0771b6885a3a",
      "name": "my-image"
  },
  "url": "https://example.com/foo.raw",
  "status": "failed"
}

CUSTOM_IMAGE_IMPORT_RESP_SUCCESS = {
  "href": "https://api.cloudscale.ch/v1/custom-images/import/11111111-1864-4608-853a-0771b6885a3a",
  "uuid": "11111111-1864-4608-853a-0771b6885a3a",
  "custom_image": {
      "href": "https://api.cloudscale.ch/v1/custom-images/11111111-1864-4608-853a-0771b6885a3a",
      "uuid": "11111111-1864-4608-853a-0771b6885a3a",
      "name": "my-image"
  },
  "url": "https://example.com/foo.raw",
  "status": "success"
}

@responses.activate
def test_custom_images_get_all():
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + '/custom-images',
        json=[CUSTOM_IMAGE_RESP],
        status=200)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a',
        'token',
        'custom-image',
        'list',
    ])
    assert result.exit_code == 0

@responses.activate
def test_custom_images_get_by_uuid():
    uuid = "11111111-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + '/custom-images/' + uuid,
        json=CUSTOM_IMAGE_RESP,
        status=200)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'custom-image',
        'show',
        uuid,
    ])
    assert result.exit_code == 0

@responses.activate
def test_custom_images_delete():
    uuid = "11111111-1864-4608-853a-0771b6885a3a"
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + '/custom-images/' + uuid,
        json=CUSTOM_IMAGE_RESP,
        status=200)
    responses.add(
        responses.DELETE,
        CLOUDSCALE_API_URL + '/custom-images/' + uuid,
        status=204)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'custom-image',
        'delete',
        uuid,
    ])
    assert result.exit_code == 1
    result = runner.invoke(cli, [
        '-a', 'token',
        'custom-image',
        'delete',
        uuid,
        '--force',

    ])
    assert result.exit_code == 0

@responses.activate
def test_custom_images_import():
    uuid = "11111111-1864-4608-853a-0771b6885a3a"
    name = "my-image"
    responses.add(
        responses.POST,
        CLOUDSCALE_API_URL + '/custom-images/import',
        json=CUSTOM_IMAGE_IMPORT_RESP,
        status=201)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + '/custom-images/import/' + uuid,
        json=CUSTOM_IMAGE_IMPORT_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + '/custom-images/import/' + uuid,
        json=CUSTOM_IMAGE_IMPORT_RESP_FAILED,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + '/custom-images/import/' + uuid,
        json=CUSTOM_IMAGE_IMPORT_RESP,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + '/custom-images/import/' + uuid,
        json=CUSTOM_IMAGE_IMPORT_RESP_SUCCESS,
        status=200)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + '/custom-images/' + uuid,
        json=CUSTOM_IMAGE_RESP,
        status=200)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'custom-image',
        'import',
        '--name',
        name,
        '--url',
        'https://example.com/example.raw',
        '--slug',
        'my-image-slug',
        '--zone',
        'lpg1',
        '--user-data-handling',
        'pass-through',
    ])
    assert result.exit_code == 0

    result = runner.invoke(cli, [
        '-a', 'token',
        'custom-image',
        'import',
        '--name',
        name,
        '--url',
        'https://example.com/example.raw',
        '--slug',
        'my-image-slug',
        '--zone',
        'lpg1',
        '--user-data-handling',
        'pass-through',
        '--wait'
    ])
    assert result.exit_code == 1

    result = runner.invoke(cli, [
        '-a', 'token',
        'custom-image',
        'import',
        '--name',
        name,
        '--url',
        'https://example.com/example.raw',
        '--slug',
        'my-image-slug',
        '--zone',
        'lpg1',
        '--user-data-handling',
        'pass-through',
        '--wait'
    ])
    assert result.exit_code == 0

@responses.activate
def test_custom_images_update():
    uuid = "11111111-1864-4608-853a-0771b6885a3a"
    name = "my-image"
    responses.add(
        responses.PATCH,
        CLOUDSCALE_API_URL + '/custom-images/' + uuid,
        json=CUSTOM_IMAGE_RESP,
        status=204)
    responses.add(
        responses.GET,
        CLOUDSCALE_API_URL + '/custom-images/' + uuid,
        json=CUSTOM_IMAGE_RESP,
        status=200)

    runner = CliRunner()
    result = runner.invoke(cli, [
        '-a', 'token',
        'custom-image',
        'update',
        uuid,
        '--name',
        name,
        '--slug',
        'my-image-slug',
    ])
    assert result.exit_code == 0
