import re

class NetworkParserError(BaseException):
    pass


class CloudscaleNetworkInterface():
    def __init__(self):
        self._uuid = None
        # List of addresses in the form:
        # [{subnet: UUID1, address: IPv4}, {subnet: UUID2, address: IPv4)]
        # start with empty list
        self._addresses = []
        self.assign_address = True

    def set_uuid(self, uuid):
        self._uuid = uuid

    def add_subnet(self, uuid, address):
        if uuid and address:
            self._addresses.append({"subnet": uuid, "address": address})
        elif uuid:
            self._addresses.append({"subnet": uuid})
        else:
            self._addresses.append({"address": address})

    def as_json(self):
        if self._uuid and not self._addresses and self.assign_address:
            return {'network': self._uuid}
        elif self._uuid and self._addresses and self.assign_address:
            return {'network': self._uuid, 'addresses': self._addresses}
        elif not self._uuid and self.assign_address:
            return {'addresses': self._addresses}
        elif self._uuid and not self.assign_address:
            return {'network': self._uuid, 'addresses': []}
        raise NetworkParserError("Cannot create json string out of your interface definiton")


class CloudscaleInterfaceParameterParser():
    def __init__(self, string):
        self._string = string
        self._cursor = 0

    def peek_strings(self, *args):
        for arg in args:
            if self._string[self._cursor:].startswith(arg):
                return arg

    def expect_string(self, arg):
        if arg and self._string[self._cursor:].startswith(arg):
            self._cursor += len(arg)
            return arg
        else:
            raise NetworkParserError(f"Expected {arg}, but found {self._string[self._cursor:]} at position {self._cursor}")

    def expect_uuid(self):
        m = re.match(r'(^[\w-]*)', self._string[self._cursor:])
        try:
            uuid = str(m.group(0))
            self._cursor += len(uuid)
            return uuid
        except Exception:
            raise NetworkParserError(f"Expected valid UUID, but found {self._string[self._cursor:]}")

    def expect_address(self):
        m = re.match(r'(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', self._string[self._cursor:])
        try:
            address = str(m.group(0))
            self._cursor += len(address)
            return address
        except Exception:
            raise NetworkParserError(f"Expected valid IPv4 Address, but found {self._string[self._cursor:]}")

    def expect_string_or_uuid(self, arg=None):
        try:
            return self.expect_string(arg)
        except NetworkParserError:
            try:
                return self.expect_uuid()
            except NetworkParserError:
                raise NetworkParserError(f"Expected UUID or {arg}, but found {self._string[self._cursor:]} at position {self._cursor}")

    def expect_end(self):
        if self._cursor != len(self._string):
            raise NetworkParserError(f"Expected the end, but found '{self._string[self._cursor:]}'")

    def has_empty_address(self):
        if self._string[self._cursor:] == 'address=':
            return True
        else:
            return False

    def parse_address(self):
        self.expect_string('address=')
        return self.expect_address()

    def parse_subnet(self):
        self.expect_string('subnet=')
        uuid = self.expect_string_or_uuid()
        if self.peek_strings(')', ',', '') == ',':
            self.expect_string(',')
            return uuid, self.parse_address()
        return uuid, None

def parse_interface(string):
    parser = CloudscaleInterfaceParameterParser(string)
    interface = CloudscaleNetworkInterface()
    type_ = parser.peek_strings('network', 'subnet')
    if type_ == 'network':
        parser.expect_string('network')
        parser.expect_string('=')
        interface.set_uuid(parser.expect_string_or_uuid('public'))
        if parser.peek_strings(',') == ',':
            parser.expect_string(',')
            if parser.peek_strings('(') != '(':
                type_ = parser.peek_strings('subnet', 'address')
                if type_ == 'subnet':
                    subnet, address = parser.parse_subnet()
                    interface.add_subnet(subnet, address)
                elif type_ == 'address':
                    if parser.has_empty_address():
                        parser.expect_string('address=')
                        interface.assign_address = False
                    else:
                        subnet = None
                        address = parser.parse_address()
                        interface.add_subnet(subnet, address)
            else:
                while parser.peek_strings('(') == '(':
                    parser.expect_string('(')
                    subnet, address = parser.parse_subnet()
                    interface.add_subnet(subnet, address)
                    parser.expect_string(')')
                    if parser.peek_strings(',') == ',':
                        parser.expect_string(',')
    elif type_ == 'subnet':
        subnet, address = parser.parse_subnet()
        interface.add_subnet(subnet, address)

    parser.expect_end()
    return interface
