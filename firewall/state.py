import time
from datetime import datetime


# Only these protocols have ports, so only these can be tracked.
TRACKED_PROTOCOLS = ("TCP", "UDP")

# Seconds of silence after which a connection is forgotten.
DEFAULT_TIMEOUT = 300


class Connection:
    """
    One remembered conversation.

    The side that sent the FIRST (allowed) packet is the "initiator".
    Packets going the same way are FORWARD traffic; packets going
    back the other way are REPLY traffic.
    """

    def __init__(
        self,
        source_ip,
        source_port,
        destination_ip,
        destination_port,
        protocol,
        now=None
    ):

        self.source_ip = source_ip
        self.source_port = source_port

        self.destination_ip = destination_ip
        self.destination_port = destination_port

        self.protocol = protocol

        self.state = "ESTABLISHED"

        self.created_at = datetime.now()
        self.last_seen = time.time() if now is None else now

        self.forward_packets = 1
        self.reply_packets = 0

    def direction(
        self,
        source_ip,
        source_port,
        destination_ip,
        destination_port,
        protocol
    ):
        """
        Return "FORWARD", "REPLY", or None if the packet
        does not belong to this connection.
        """

        if self.protocol != protocol:
            return None

        if (
            self.source_ip == source_ip
            and self.source_port == source_port
            and self.destination_ip == destination_ip
            and self.destination_port == destination_port
        ):
            return "FORWARD"

        if (
            self.source_ip == destination_ip
            and self.source_port == destination_port
            and self.destination_ip == source_ip
            and self.destination_port == source_port
        ):
            return "REPLY"

        return None

    def matches(
        self,
        source_ip,
        source_port,
        destination_ip,
        destination_port,
        protocol
    ):
        """
        True if the packet belongs to this connection
        (same direction or the reverse direction).
        """

        return self.direction(
            source_ip,
            source_port,
            destination_ip,
            destination_port,
            protocol
        ) is not None

    def __str__(self):
        return (
            f"{self.source_ip}:{self.source_port} → "
            f"{self.destination_ip}:{self.destination_port} "
            f"/ {self.protocol}  [{self.state}]"
        )


class StatefulFirewall:
    """
    Connection table.

    Connections are stored in a dictionary so lookups are fast, and
    idle connections expire after `timeout` seconds. `clock` can be
    replaced in tests so time can be moved forward artificially.
    """

    def __init__(self, timeout=DEFAULT_TIMEOUT, clock=time.time):
        self.timeout = timeout
        self._clock = clock
        self._connections = {}

    # ---------- helpers ----------

    @staticmethod
    def is_trackable(protocol, *ports):
        """
        A packet can be tracked only if it is TCP/UDP
        and every port needed is known.
        """

        return (
            protocol in TRACKED_PROTOCOLS
            and all(port is not None for port in ports)
        )

    @staticmethod
    def _key(
        source_ip,
        source_port,
        destination_ip,
        destination_port,
        protocol
    ):
        """
        Direction-independent key: A->B and B->A give the same key.
        """

        endpoints = sorted([
            (source_ip, source_port),
            (destination_ip, destination_port)
        ])

        return (protocol, endpoints[0], endpoints[1])

    @property
    def connections(self):
        return list(self._connections.values())

    # ---------- public API ----------

    def seconds_remaining(self, connection):
        """
        Seconds left before an idle connection expires.
        """

        return self.timeout - (self._clock() - connection.last_seen)

    def purge_expired(self):
        """
        Remove connections idle for longer than the timeout.
        Returns how many were removed.
        """

        now = self._clock()

        expired = [
            key for key, connection in self._connections.items()
            if now - connection.last_seen > self.timeout
        ]

        for key in expired:
            del self._connections[key]

        return len(expired)

    def create_connection(
        self,
        source_ip,
        source_port,
        destination_ip,
        destination_port,
        protocol
    ):
        """
        Remember a new conversation (or refresh it if it exists).
        """

        key = self._key(
            source_ip,
            source_port,
            destination_ip,
            destination_port,
            protocol
        )

        existing = self._connections.get(key)

        if existing is not None:
            existing.last_seen = self._clock()
            return existing

        connection = Connection(
            source_ip,
            source_port,
            destination_ip,
            destination_port,
            protocol,
            now=self._clock()
        )

        self._connections[key] = connection

        return connection

    def lookup(
        self,
        source_ip,
        source_port,
        destination_ip,
        destination_port,
        protocol,
        refresh=False
    ):
        """
        Find the connection a packet belongs to.

        Returns (connection, direction) or (None, None).
        With refresh=True the idle timer is reset and the
        packet counters are updated.
        """

        self.purge_expired()

        key = self._key(
            source_ip,
            source_port,
            destination_ip,
            destination_port,
            protocol
        )

        connection = self._connections.get(key)

        if connection is None:
            return None, None

        direction = connection.direction(
            source_ip,
            source_port,
            destination_ip,
            destination_port,
            protocol
        )

        if direction is None:
            return None, None

        if refresh:
            connection.last_seen = self._clock()

            if direction == "FORWARD":
                connection.forward_packets += 1
            else:
                connection.reply_packets += 1

        return connection, direction

    def connection_exists(
        self,
        source_ip,
        source_port,
        destination_ip,
        destination_port,
        protocol
    ):
        connection, _ = self.lookup(
            source_ip,
            source_port,
            destination_ip,
            destination_port,
            protocol
        )

        return connection is not None

    def clear_connections(self):
        self._connections.clear()

    def get_connections(self):
        self.purge_expired()
        return list(self._connections.values())
