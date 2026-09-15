from dataclasses import dataclass
import ipaddress


@dataclass
class Packet:
    source_ip: str
    destination_ip: str
    port: int
    protocol: str

    def validate(self):
        """
        Validate all packet fields.
        Returns:
            (True, "Valid packet")
        or:
            (False, "Error message")
        """

        # Validate source IP
        try:
            ipaddress.ip_address(self.source_ip)
        except ValueError:
            return False, f"Invalid source IP: {self.source_ip}"

        # Validate destination IP
        try:
            ipaddress.ip_address(self.destination_ip)
        except ValueError:
            return False, f"Invalid destination IP: {self.destination_ip}"

        # Validate port
        if not isinstance(self.port, int):
            return False, "Port must be an integer."

        if self.port < 0 or self.port > 65535:
            return False, "Port must be between 0 and 65535."

        # Validate protocol
        allowed_protocols = ["TCP", "UDP", "ICMP"]

        if self.protocol.upper() not in allowed_protocols:
            return False, (
                f"Invalid protocol. Use: "
                f"{', '.join(allowed_protocols)}"
            )

        return True, "Valid packet"

    def normalized(self):
        """
        Return a normalized version of the packet.
        """

        return Packet(
            source_ip=self.source_ip.strip(),
            destination_ip=self.destination_ip.strip(),
            port=int(self.port),
            protocol=self.protocol.upper().strip()
        )

    def to_dict(self):
        """
        Convert packet into dictionary.
        """

        return {
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "port": self.port,
            "protocol": self.protocol
        }

    def __str__(self):
        return (
            f"{self.source_ip} → "
            f"{self.destination_ip} : "
            f"{self.port} / "
            f"{self.protocol}"
        )