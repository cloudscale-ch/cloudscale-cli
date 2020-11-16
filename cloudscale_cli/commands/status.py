import sys
import click

from ..util import to_table
import requests

@click.command()
def status():
    try:
        response = requests.get('https://cloudscale-status.net/api/v1/components')
        data = response.json().get('data')
        data.sort(key=lambda x: x.get('order'))
        click.echo(to_table(data, ['name', 'status_name', 'updated_at', 'description']))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
