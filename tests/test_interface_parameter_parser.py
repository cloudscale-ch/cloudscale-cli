import pytest
import cloudscale_cli.interface_parameter_parser as p

@pytest.mark.parametrize(
    'input, output, error', [
        (
            'network=public',
            {'network': 'public'},
            None
        ),
        (
            'network=2db69ba3-1864-4608-853a-0771b6885a3a',
            {'network': '2db69ba3-1864-4608-853a-0771b6885a3a'},
            None
        ),
        (
            'subnet=8e79cc58-dc9f-4f68-aeae-e0eac3f06f16',
            {'addresses': [{'subnet': '8e79cc58-dc9f-4f68-aeae-e0eac3f06f16'}]},
            None
        ),
        (
            'network=9a23808b-dd19-480f-9f55-5a945da4e819,subnet=8e79cc58-dc9f-4f68-aeae-e0eac3f06f16',
            {'network': '9a23808b-dd19-480f-9f55-5a945da4e819', 'addresses': [{'subnet': '8e79cc58-dc9f-4f68-aeae-e0eac3f06f16'}]},
            None
        ),
        (
            'subnet=91dbef92-ddb1-47e0-8625-73326792d3e1,address=172.26.241.14',
            {'addresses': [{'subnet': '91dbef92-ddb1-47e0-8625-73326792d3e1', 'address': '172.26.241.14'}]},
            None
        ),
        (
            'network=9a23808b-dd19-480f-9f55-5a945da4e819,subnet=8e79cc58-dc9f-4f68-aeae-e0eac3f06f16,address=172.21.67.54',
            {'network': '9a23808b-dd19-480f-9f55-5a945da4e819', 'addresses': [{'subnet': '8e79cc58-dc9f-4f68-aeae-e0eac3f06f16', 'address': '172.21.67.54'}]},
            None
        ),
        (
            'network=9a23808b-dd19-480f-9f55-5a945da4e819,address=',
            {'network': '9a23808b-dd19-480f-9f55-5a945da4e819', 'addresses': []},
            None
        ),
        (
            'network=9a23808b-dd19-480f-9f55-5a945da4e819,subnet=8e79cc58-dc9f-4f68-aeae-e0eac3f06f16,address=',
            None,
            "Expected valid IPv4 address, but found ''"
        ),
        (
            'subnet=9a23808b-dd19-480f-9f55-5a945da4e819,address=',
            None,
            "Expected valid IPv4 address, but found ''"
        ),
        (
            'subnet=91dbef92,address=172.26.241.14',
            None,
            "Expected UUID or 'None', but found '91dbef92,address=172.26.241.14' at position 7"
        ),
        (
            'subnet=91dbef92-ddb1-47e0-8625-73326792d3e1,address=172.2226.241,XX',
            None,
            "Expected valid IPv4 address, but found '172.2226.241,XX'"
        ),
        (
            'network=91dbef92-ddb1-47e0-8625-73326792d3e1,aaa',
            None,
            "Expected the end, but found 'aaa'"
        ),
        ('foo', None, "Expected the end, but found 'foo'"),
        ('network=foo', None, "Expected UUID or 'public', but found 'foo' at position 8")
    ]
)

def test_parser(input, output, error):
    if error is None:
        assert p.parse_interface(input).as_json() == output
    else:
        with pytest.raises(p.NetworkParserError) as e:
            p.parse_interface(input)
        assert str(e.value) == error
