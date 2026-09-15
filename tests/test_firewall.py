import unittest

from firewall.packet import Packet
from firewall.rules import FirewallRule, RuleManager
from firewall.engine import FirewallEngine


class TestFirewall(unittest.TestCase):

    def setUp(self):

        self.rule_manager = RuleManager(
            "data/test_rules.json"
        )

        self.rule_manager.rules = [
            FirewallRule(
                "192.168.1.10",
                "*",
                "80",
                "TCP",
                "ALLOW"
            ),

            FirewallRule(
                "192.168.1.20",
                "*",
                "23",
                "TCP",
                "BLOCK"
            ),

            FirewallRule(
                "*",
                "*",
                "443",
                "TCP",
                "ALLOW"
            )
        ]

        self.engine = FirewallEngine(
            self.rule_manager
        )

    def test_allowed_http(self):

        packet = Packet(
            "192.168.1.10",
            "192.168.1.100",
            80,
            "TCP"
        )

        result = self.engine.evaluate(
            packet
        )

        self.assertEqual(
            result["action"],
            "ALLOW"
        )

    def test_blocked_telnet(self):

        packet = Packet(
            "192.168.1.20",
            "192.168.1.100",
            23,
            "TCP"
        )

        result = self.engine.evaluate(
            packet
        )

        self.assertEqual(
            result["action"],
            "BLOCK"
        )

    def test_allowed_https(self):

        packet = Packet(
            "192.168.1.50",
            "192.168.1.100",
            443,
            "TCP"
        )

        result = self.engine.evaluate(
            packet
        )

        self.assertEqual(
            result["action"],
            "ALLOW"
        )

    def test_default_block(self):

        packet = Packet(
            "192.168.1.50",
            "192.168.1.100",
            5555,
            "TCP"
        )

        result = self.engine.evaluate(
            packet
        )

        self.assertEqual(
            result["action"],
            "BLOCK"
        )

    def test_wildcard_rule(self):

        rule = FirewallRule(
            "*",
            "*",
            "443",
            "TCP",
            "ALLOW"
        )

        packet = Packet(
            "10.10.10.10",
            "172.16.0.1",
            443,
            "TCP"
        )

        self.assertTrue(
            rule.matches(packet)
        )

    def test_rule_priority(self):

        manager = RuleManager(
            "data/test_priority.json"
        )

        manager.rules = [

            FirewallRule(
                "192.168.1.50",
                "*",
                "80",
                "TCP",
                "BLOCK"
            ),

            FirewallRule(
                "*",
                "*",
                "80",
                "TCP",
                "ALLOW"
            )
        ]

        engine = FirewallEngine(
            manager
        )

        packet = Packet(
            "192.168.1.50",
            "192.168.1.100",
            80,
            "TCP"
        )

        result = engine.evaluate(
            packet
        )

        self.assertEqual(
            result["action"],
            "BLOCK"
        )

    def test_invalid_ip(self):

        packet = Packet(
            "999.999.999.999",
            "192.168.1.100",
            80,
            "TCP"
        )

        result = self.engine.evaluate(
            packet
        )

        self.assertEqual(
            result["action"],
            "BLOCK"
        )


if __name__ == "__main__":
    unittest.main()