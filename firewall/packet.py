from dataclasses import dataclass
from typing import Optional, Dict, Any
import ipaddress


@dataclass
class Packet:
    """
    A simulated network packet.

    port        = DESTINATION port (this is what firewall rules match on)
    source_port = the sender's port (optional). It is only needed for
                  stateful connection tracking, so existing code that
                  builds Packet(src, dst, port, protocol) keeps working.
    """

    source_ip: str
    destination_ip: str
    port: int
    protocol: str
    source_port: Optional[int] = None
    packet_id: Optional[str] = None
    sequence: Optional[int] = None
    purpose: Optional[str] = None
    explanation: Optional[str] = None
    flow_id: Optional[str] = None
    direction: Optional[str] = None
    payload_summary: Optional[str] = None
    tcp_flags: Optional[str] = None

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

        # Validate destination port
        if not isinstance(self.port, int):
            return False, "Port must be an integer."

        if self.port < 0 or self.port > 65535:
            return False, "Port must be between 0 and 65535."

        # Validate source port (optional)
        if self.source_port is not None:
            if not isinstance(self.source_port, int):
                return False, "Source port must be an integer."

            if self.source_port < 0 or self.source_port > 65535:
                return False, "Source port must be between 0 and 65535."

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
            protocol=self.protocol.upper().strip(),
            source_port=(
                None if self.source_port is None
                else int(self.source_port)
            ),
            packet_id=self.packet_id,
            sequence=self.sequence,
            purpose=self.purpose,
            explanation=self.explanation,
            flow_id=self.flow_id,
            direction=self.direction,
            payload_summary=self.payload_summary,
            tcp_flags=self.tcp_flags
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert packet into dictionary.
        """

        return {
            "packet_id": self.packet_id or "PKT-000",
            "sequence": self.sequence or 0,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "port": self.port,
            "protocol": self.protocol,
            "source_port": self.source_port,
            "purpose": self.purpose or "Simulated Traffic",
            "explanation": self.explanation or "",
            "flow_id": self.flow_id or "",
            "direction": self.direction or ("INBOUND" if self.destination_ip.startswith("192.168.") else "OUTBOUND"),
            "payload_summary": self.payload_summary or f"{self.protocol} payload ({self.port})",
            "tcp_flags": self.tcp_flags or ("SYN" if self.protocol == "TCP" and not self.direction == "REPLY" else "ACK"),
            "raw_format": self.to_raw_format()
        }

    def to_raw_format(self) -> str:
        """
        Generates realistic tcpdump / raw wire packet disassembly format.
        Displayed when a user double-clicks any packet.
        """
        src = f"{self.source_ip}:{self.source_port}" if self.source_port is not None else self.source_ip
        dst = f"{self.destination_ip}:{self.port}"
        proto = self.protocol.upper()
        flags = f" [{self.tcp_flags}]" if self.tcp_flags else ""
        flow = f" (flow={self.flow_id})" if self.flow_id else ""
        purpose = f" // {self.purpose}" if self.purpose else ""
        
        # Simulated raw frame header & hex dump
        hex_src = "".join([f"{int(x):02x}" for x in self.source_ip.split(".")]) if "." in self.source_ip and len(self.source_ip.split(".")) == 4 else "00000000"
        hex_dst = "".join([f"{int(x):02x}" for x in self.destination_ip.split(".")]) if "." in self.destination_ip and len(self.destination_ip.split(".")) == 4 else "ffffffff"
        hex_sport = f"{(self.source_port or 0):04x}"
        hex_dport = f"{self.port:04x}"

        lines = [
            f"Frame {self.sequence or 1}: {len(src + dst) + 40} bytes on wire ({self.packet_id or 'PKT-000'})",
            f"Internet Protocol Version 4, Src: {self.source_ip}, Dst: {self.destination_ip}",
            f"    0100 .... = Version: 4",
            f"    .... 0101 = Header Length: 20 bytes (5)",
            f"    Total Length: 64",
            f"    Protocol: {proto} ({6 if proto == 'TCP' else 17 if proto == 'UDP' else 1})",
            f"    Source Address: {self.source_ip}",
            f"    Destination Address: {self.destination_ip}",
        ]
        if proto in ("TCP", "UDP"):
            lines.extend([
                f"{'Transmission Control Protocol' if proto == 'TCP' else 'User Datagram Protocol'}, Src Port: {self.source_port or 0}, Dst Port: {self.port}",
                f"    Source Port: {self.source_port or 0}",
                f"    Destination Port: {self.port}",
            ])
            if proto == "TCP":
                lines.append(f"    Flags: {self.tcp_flags or 'SYN'} ({flags.strip()})")
        elif proto == "ICMP":
            lines.extend([
                "Internet Control Message Protocol",
                f"    Type: 8 (Echo (ping) request)" if not self.direction == "REPLY" else "    Type: 0 (Echo (ping) reply)",
                "    Code: 0"
            ])
        lines.append("")
        lines.append("Raw Frame Dump (Hex & ASCII):")
        lines.append(f"0000   45 00 00 3c 1c 46 40 00  40 {0x06 if proto == 'TCP' else 0x11:02x} b7 89 {hex_src[:4]} {hex_src[4:]}   E..<.@.@....{self.protocol[:2]}..")
        lines.append(f"0010   {hex_dst[:4]} {hex_dst[4:]} {hex_sport} {hex_dport}  00 00 00 00 00 00 00 00   ..........{self.port % 100}..")
        if self.payload_summary:
            lines.append(f"Payload: {self.payload_summary}{purpose}{flow}")

        return "\n".join(lines)

    def __str__(self):
        source = (
            self.source_ip if self.source_port is None
            else f"{self.source_ip}:{self.source_port}"
        )

        return (
            f"{source} → "
            f"{self.destination_ip} : "
            f"{self.port} / "
            f"{self.protocol}"
        )
