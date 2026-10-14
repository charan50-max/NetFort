import time
from firewall.packet import Packet
from firewall.rules import RuleManager
from firewall.state import StatefulFirewall


class FirewallEngine:

    def __init__(
        self,
        rule_manager,
        stateful_firewall=None,
        stateful_enabled=True
    ):
        self.rule_manager = rule_manager

        self.stateful = (
            stateful_firewall
            if stateful_firewall is not None
            else StatefulFirewall()
        )
        self.stateful_enabled = stateful_enabled

        self.total_packets = 0
        self.allowed_packets = 0
        self.blocked_packets = 0
        self.invalid_packets = 0
        self.default_blocked_packets = 0
        self.rule_allowed_packets = 0
        self.rule_blocked_packets = 0
        self.stateful_allowed_packets = 0

    def reset_statistics(self):
        """
        Reset packet statistics.
        """

        self.total_packets = 0
        self.allowed_packets = 0
        self.blocked_packets = 0
        self.invalid_packets = 0
        self.default_blocked_packets = 0
        self.rule_allowed_packets = 0
        self.rule_blocked_packets = 0
        self.stateful_allowed_packets = 0

    def reset_connections(self):
        """
        Forget all tracked connections.
        Call this after rules change, so old connections
        cannot outlive the rules that allowed them.
        """

        self.stateful.clear_connections()

    def evaluate(self, packet):
        """
        Evaluate a packet.

        Order of checks:
          1. Normalize + validate the packet
          2. Stateful check: does it belong to an existing connection?
          3. Rules, top to bottom (first match wins)
          4. Default policy = BLOCK

        Returns a dictionary containing:
        action
        matched_rule        (None when decided by state or default, 1-based index when matched)
        reason
        connection_state    ("NEW", "ESTABLISHED", "REPLY" or None)
        reason_code
        matched_rule_id
        matched_rule_name
        processing_time_ms
        """
        start_time = time.perf_counter()
        self.total_packets += 1

        packet = packet.normalized()
        valid, message = packet.validate()

        if not valid:
            self.blocked_packets += 1
            self.invalid_packets += 1
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

            return {
                "action": "BLOCK",
                "matched_rule": None,
                "matched_rule_id": None,
                "matched_rule_name": None,
                "reason_code": "INVALID_PACKET",
                "reason": message,
                "connection_state": None,
                "processing_time_ms": elapsed_ms,
                "packet_id": packet.packet_id
            }

        # Only TCP/UDP packets with a known source port can be tracked
        trackable = (
            self.stateful_enabled
            and self.stateful.is_trackable(
                packet.protocol,
                packet.source_port
            )
        )

        # ---- Stateful check (before the rules) ----
        if trackable:
            connection, direction = self.stateful.lookup(
                packet.source_ip,
                packet.source_port,
                packet.destination_ip,
                packet.port,
                packet.protocol,
                refresh=True
            )

            if connection is not None:
                self.allowed_packets += 1
                self.stateful_allowed_packets += 1
                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

                return {
                    "action": "ALLOW",
                    "matched_rule": None,
                    "matched_rule_id": None,
                    "matched_rule_name": None,
                    "reason_code": "ESTABLISHED_CONNECTION",
                    "reason": (
                        "Part of an established connection "
                        f"({direction.lower()} traffic)."
                    ),
                    "connection_state": "ESTABLISHED",
                    "processing_time_ms": elapsed_ms,
                    "packet_id": packet.packet_id
                }

        # ---- Rules: first matching rule wins ----
        for index, rule in enumerate(self.rule_manager.rules):
            if rule.matches(packet):
                connection_state = None
                rule_id = getattr(rule, "rule_id", f"RULE-{index + 1}")
                rule_name = getattr(rule, "name", f"Rule #{index + 1}")

                if rule.action == "ALLOW":
                    self.allowed_packets += 1
                    self.rule_allowed_packets += 1

                    # An allowed new packet starts a connection,
                    # so its replies will be recognised later.
                    if trackable:
                        self.stateful.create_connection(
                            packet.source_ip,
                            packet.source_port,
                            packet.destination_ip,
                            packet.port,
                            packet.protocol
                        )
                        connection_state = "NEW"
                    reason_code = "RULE_ALLOW"
                else:
                    self.blocked_packets += 1
                    self.rule_blocked_packets += 1
                    reason_code = "RULE_BLOCK"

                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

                return {
                    "action": rule.action,
                    "matched_rule": index + 1,
                    "matched_rule_id": rule_id,
                    "matched_rule_name": rule_name,
                    "reason_code": reason_code,
                    "reason": f"Matched firewall rule #{index + 1} ({rule_name})",
                    "connection_state": connection_state,
                    "processing_time_ms": elapsed_ms,
                    "packet_id": packet.packet_id
                }

        # Default policy = BLOCK
        self.blocked_packets += 1
        self.default_blocked_packets += 1
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 3)

        return {
            "action": "BLOCK",
            "matched_rule": None,
            "matched_rule_id": None,
            "matched_rule_name": None,
            "reason_code": "DEFAULT_BLOCK",
            "reason": "No matching rule. Default policy is BLOCK.",
            "connection_state": None,
            "processing_time_ms": elapsed_ms,
            "packet_id": packet.packet_id
        }

    def get_statistics(self):
        """
        Return firewall statistics.
        """

        total = self.total_packets

        if total == 0:
            block_rate = 0.0
            allow_rate = 0.0
        else:
            block_rate = round((self.blocked_packets / total) * 100, 2)
            allow_rate = round((self.allowed_packets / total) * 100, 2)

        return {
            "total": self.total_packets,
            "allowed": self.allowed_packets,
            "blocked": self.blocked_packets,
            "allow_rate": allow_rate,
            "block_rate": block_rate,
            "invalid_packets": self.invalid_packets,
            "default_blocks": self.default_blocked_packets,
            "rule_allows": self.rule_allowed_packets,
            "rule_blocks": self.rule_blocked_packets,
            "stateful_allows": self.stateful_allowed_packets,
            "active_connections": len(self.stateful.get_connections()) if self.stateful_enabled else 0
        }
