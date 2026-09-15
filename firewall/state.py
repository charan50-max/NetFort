from datetime import datetime


class Connection:

    def __init__(
        self,
        source_ip,
        source_port,
        destination_ip,
        destination_port,
        protocol
    ):

        self.source_ip = source_ip
        self.source_port = source_port

        self.destination_ip = destination_ip
        self.destination_port = destination_port

        self.protocol = protocol

        self.state = "ESTABLISHED"

        self.created_at = datetime.now()

    def matches(
        self,
        source_ip,
        source_port,
        destination_ip,
        destination_port,
        protocol
    ):

        normal_direction = (
            self.source_ip == source_ip
            and self.source_port == source_port
            and self.destination_ip == destination_ip
            and self.destination_port == destination_port
            and self.protocol == protocol
        )

        reverse_direction = (
            self.source_ip == destination_ip
            and self.source_port == destination_port
            and self.destination_ip == source_ip
            and self.destination_port == source_port
            and self.protocol == protocol
        )

        return normal_direction or reverse_direction


class StatefulFirewall:

    def __init__(self):
        self.connections = []

    def create_connection(
        self,
        source_ip,
        source_port,
        destination_ip,
        destination_port,
        protocol
    ):

        connection = Connection(
            source_ip,
            source_port,
            destination_ip,
            destination_port,
            protocol
        )

        self.connections.append(connection)

        return connection

    def connection_exists(
        self,
        source_ip,
        source_port,
        destination_ip,
        destination_port,
        protocol
    ):

        for connection in self.connections:

            if connection.matches(
                source_ip,
                source_port,
                destination_ip,
                destination_port,
                protocol
            ):
                return True

        return False

    def clear_connections(self):
        self.connections.clear()

    def get_connections(self):
        return self.connections