import json
from click import Group
from collections import OrderedDict
from tabulate import tabulate
from pygments import highlight, lexers, formatters
import jmespath


class OrderedGroup(Group):
    '''
    A click Group with ordered command list.
    '''

    def __init__(self, name=None, commands=[], **attrs):
        Group.__init__(self, name, **attrs)
        self.commands = OrderedDict(commands)

    def list_commands(self, ctx):
        return sorted(self.commands.keys())


def to_table(data: list, headers: list, format_json: str = None) -> str:
    '''
    Turn a list into a table
    '''

    if format_json:
        data = jmespath.search(format_json, data)

    formated_headers = []

    cols = list()
    for d in data:
        rows = list()
        for header in headers:
            if header not in d:
                continue

            formated_headers.append(header.upper().replace('_', ' '))

            if header == 'tags':
                row = ', '.join(['%s=%s' % (k, v) for k, v in d[header].items()])

            elif isinstance(d[header], dict):
                if 'name' in d[header]:
                    row = d[header]['name']
                elif 'slug' in d[header]:
                    row = d[header]['slug']

            elif isinstance(d[header], list):
                row_list = []
                for i in d[header]:
                    if isinstance(i, dict):
                        if 'slug' in i:
                            row_list.append(i['slug'])
                        elif 'name' in i:
                            row_list.append(i['name'])
                    else:
                        row_list.append(i)

                row = ', '.join(row_list)

            else:
                row = d[header]

            rows.append(row)
        cols.append(rows)

    result = tabulate(cols, headers=formated_headers)
    return result

def to_pretty_json(data: dict) -> tuple:
    '''
    Format JSON to human readable.
    '''
    result = json.dumps(data, sort_keys=True, indent=4)
    result = highlight(result, lexers.JsonLexer(), formatters.TerminalFormatter())
    return result

def tags_to_dict(data: tuple) -> dict:
    '''
    Split a tuple of tags (key=value) into a dict.
    '''
    if not data:
        return

    result = dict()
    for d in data:
        if '=' not in d:
            raise ValueError("Invalid tag '{}'. Use the format 'name=value'.".format(d))

        k, v = d.split('=', maxsplit=1)
        result[k] = v
    return result
