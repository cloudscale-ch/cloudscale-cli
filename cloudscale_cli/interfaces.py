"""Parser for the ``--interface`` option of the server commands.

An interface is described by a small syntax, e.g.::

    network=public
    network=<uuid>,subnet=<uuid>,address=<ipv4>
    (subnet=<uuid>,address=<ipv4>),(subnet=<uuid>,address=<ipv4>)

which is turned into the JSON structure expected by the API.
"""

import re

UUID_RE = re.compile(r"^[\w]*-[\w]*-[\w]*-[\w]*-[\w]*")
IPV4_RE = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")


class NetworkParserError(Exception):
    """Raised when an interface definition can not be understood."""


class CloudscaleNetworkInterface:
    """A network interface as it is sent to the API."""

    def __init__(self):
        self._uuid: str | None = None
        # Addresses in the form [{"subnet": <uuid>, "address": <ipv4>}, ...]
        self._addresses: list[dict[str, str]] = []
        self.assign_address = True

    def set_uuid(self, uuid: str) -> None:
        self._uuid = uuid

    def add_subnet(self, uuid: str | None, address: str | None) -> None:
        address_config = {}
        if uuid:
            address_config["subnet"] = uuid
        if address:
            address_config["address"] = address
        self._addresses.append(address_config)

    def as_json(self) -> dict:
        """Return the interface in the JSON structure of the API."""
        if not self.assign_address:
            if not self._uuid:
                raise NetworkParserError(
                    "Cannot create json string out of your interface definiton"
                )
            return {"network": self._uuid, "addresses": []}

        if not self._uuid:
            return {"addresses": self._addresses}

        if not self._addresses:
            return {"network": self._uuid}

        return {"network": self._uuid, "addresses": self._addresses}


class CloudscaleInterfaceParameterParser:
    """A cursor based parser for a single interface definition."""

    def __init__(self, string: str):
        self._string = string
        self._cursor = 0

    @property
    def _rest(self) -> str:
        return self._string[self._cursor :]

    def peek_strings(self, *args: str) -> str | None:
        """Return the first of the strings found at the cursor."""
        for arg in args:
            if self._rest.startswith(arg):
                return arg
        return None

    def expect_string(self, arg: str | None) -> str:
        if not arg or not self._rest.startswith(arg):
            raise NetworkParserError(
                f"Expected '{arg}', but found '{self._rest}' at position {self._cursor}"
            )
        self._cursor += len(arg)
        return arg

    def _expect_pattern(self, pattern: re.Pattern, expected: str) -> str:
        match = pattern.match(self._rest)
        if not match:
            raise NetworkParserError(
                f"Expected valid {expected}, but found '{self._rest}'"
            )
        self._cursor += len(match.group(0))
        return match.group(0)

    def expect_uuid(self) -> str:
        return self._expect_pattern(UUID_RE, "UUID")

    def expect_address(self) -> str:
        return self._expect_pattern(IPV4_RE, "IPv4 address")

    def expect_string_or_uuid(self, arg: str | None = None) -> str:
        """Expect either a literal string or a UUID at the cursor."""
        try:
            return self.expect_string(arg)
        except NetworkParserError:
            pass

        try:
            return self.expect_uuid()
        except NetworkParserError:
            expected = f"UUID or '{arg}'" if arg else "UUID"
            raise NetworkParserError(
                f"Expected {expected}, but found '{self._rest}' "
                f"at position {self._cursor}"
            ) from None

    def expect_end(self) -> None:
        if self._rest:
            raise NetworkParserError(f"Expected the end, but found '{self._rest}'")

    def has_empty_address(self) -> bool:
        """Whether the definition ends in ``address=``, meaning no address."""
        return self._rest == "address="

    def parse_address(self) -> str:
        self.expect_string("address=")
        return self.expect_address()

    def parse_subnet(self) -> tuple[str, str | None]:
        self.expect_string("subnet=")
        uuid = self.expect_string_or_uuid()
        if self.peek_strings(")", ",", "") == ",":
            self.expect_string(",")
            return uuid, self.parse_address()
        return uuid, None

    def parse_multiple_subnets(self, interface: CloudscaleNetworkInterface) -> None:
        while self.peek_strings("(") == "(":
            self.expect_string("(")
            subnet, address = self.parse_subnet()
            interface.add_subnet(subnet, address)
            self.expect_string(")")
            if self.peek_strings(",") == ",":
                self.expect_string(",")


def parse_interface(string: str) -> CloudscaleNetworkInterface:
    """Parse an interface definition given on the command line.

    Raises:
        NetworkParserError: The definition can not be understood.
    """
    parser = CloudscaleInterfaceParameterParser(string)
    interface = CloudscaleNetworkInterface()

    type_ = parser.peek_strings("network", "subnet", "(")
    if type_ == "network":
        _parse_network(parser, interface)
    elif type_ == "subnet":
        interface.add_subnet(*parser.parse_subnet())
    elif type_ == "(":
        if parser.peek_strings("(subnet") != "(subnet":
            raise NetworkParserError(
                "Cannot add an interface without network or subnet definition"
            )
        parser.parse_multiple_subnets(interface)
    else:
        raise NetworkParserError(
            "Cannot add an interface without network or subnet definition"
        )

    parser.expect_end()
    return interface


def _parse_network(
    parser: CloudscaleInterfaceParameterParser,
    interface: CloudscaleNetworkInterface,
) -> None:
    """Parse a definition starting with ``network=``."""
    parser.expect_string("network")
    parser.expect_string("=")
    interface.set_uuid(parser.expect_string_or_uuid("public"))

    if parser.peek_strings(",") != ",":
        return
    parser.expect_string(",")

    if parser.peek_strings("(") == "(":
        parser.parse_multiple_subnets(interface)
        return

    type_ = parser.peek_strings("subnet", "address")
    if type_ == "subnet":
        interface.add_subnet(*parser.parse_subnet())
    elif type_ == "address":
        if not parser.has_empty_address():
            raise NetworkParserError("Cannot set a fixed IP address without a subnet")
        parser.expect_string("address=")
        interface.assign_address = False
