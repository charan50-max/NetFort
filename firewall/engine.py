from firewall.packet import Packet
from firewall.rules import RuleManager


class FirewallEngine:

    def __init__(self, rule_manager):
        self.rule_manager = rule_manager

        self.total_packets = 0
        self.allowed_packets = 0
        self.blocked_packets = 0

    def reset_statistics(self):
        """
        Reset packet statistics.
        """

        self.total_packets = 0
        self.allowed_packets = 0
        self.blocked_packets = 0

    def evaluate(self, packet):
        """
        Evaluate a packet against firewall rules.

        Returns a dictionary containing:
        action
        matched_rule
        reason
        """

        self.total_packets += 1

        packet = packet.normalized()

        valid, message = packet.validate()

        if not valid:
            self.blocked_packets += 1

            return {
                "action": "BLOCK",
                "matched_rule": None,
                "reason": message
            }

        # First matching rule wins
        for index, rule in enumerate(self.rule_manager.rules):

            if rule.matches(packet):

                if rule.action == "ALLOW":
                    self.allowed_packets += 1
                else:
                    self.blocked_packets += 1

                return {
                    "action": rule.action,
                    "matched_rule": index + 1,
                    "reason": (
                        f"Matched firewall rule #{index + 1}"
                    )
                }

        # Default policy = BLOCK
        self.blocked_packets += 1

        return {
            "action": "BLOCK",
            "matched_rule": None,
            "reason": "No matching rule. Default policy is BLOCK."
        }

    def get_statistics(self):
        """
        Return firewall statistics.
        """

        total = self.total_packets

        if total == 0:
            block_rate = 0
        else:
            block_rate = (
                self.blocked_packets / total
            ) * 100

        return {
            "total": self.total_packets,
            "allowed": self.allowed_packets,
            "blocked": self.blocked_packets,
            "block_rate": block_rate
        }