import os
import tempfile
import unittest

from firewall.engine import FirewallEngine
from firewall.packet import Packet
from firewall.rules import RuleManager
from firewall.state import StatefulFirewall


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class StatefulEngineTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        rules = RuleManager(os.path.join(self.tmp.name, "rules.json"))

        self.clock = FakeClock()
        self.state = StatefulFirewall(timeout=300, clock=self.clock)
        self.engine = FirewallEngine(rules, self.state)

        # Client 192.168.1.10:5000 -> web server 192.168.1.100:80
        self.request = Packet(
            "192.168.1.10", "192.168.1.100", 80, "TCP", source_port=5000
        )
        # The server's reply goes the other way
        self.reply = Packet(
            "192.168.1.100", "192.168.1.10", 5000, "TCP", source_port=80
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_reply_blocked_without_prior_request(self):
        result = self.engine.evaluate(self.reply)
        self.assertEqual(result["action"], "BLOCK")

    def test_reply_allowed_after_request(self):
        first = self.engine.evaluate(self.request)
        self.assertEqual(first["action"], "ALLOW")
        self.assertEqual(first["matched_rule"], 1)
        self.assertEqual(first["connection_state"], "NEW")

        second = self.engine.evaluate(self.reply)
        self.assertEqual(second["action"], "ALLOW")
        self.assertIsNone(second["matched_rule"])
        self.assertEqual(second["connection_state"], "ESTABLISHED")

    def test_reply_with_wrong_port_still_blocked(self):
        self.engine.evaluate(self.request)
        spoof = Packet(
            "192.168.1.100", "192.168.1.10", 5000, "TCP", source_port=81
        )
        self.assertEqual(self.engine.evaluate(spoof)["action"], "BLOCK")

    def test_reply_with_wrong_protocol_still_blocked(self):
        self.engine.evaluate(self.request)
        udp_reply = Packet(
            "192.168.1.100", "192.168.1.10", 5000, "UDP", source_port=80
        )
        self.assertEqual(self.engine.evaluate(udp_reply)["action"], "BLOCK")

    def test_blocked_request_creates_no_state(self):
        telnet = Packet(
            "192.168.1.20", "192.168.1.100", 23, "TCP", source_port=6000
        )
        telnet_reply = Packet(
            "192.168.1.100", "192.168.1.20", 6000, "TCP", source_port=23
        )
        self.assertEqual(self.engine.evaluate(telnet)["action"], "BLOCK")
        self.assertEqual(self.engine.evaluate(telnet_reply)["action"], "BLOCK")
        self.assertEqual(self.engine.get_statistics()["active_connections"], 0)

    def test_connection_expires_after_timeout(self):
        self.engine.evaluate(self.request)
        self.clock.advance(301)
        self.assertEqual(self.engine.evaluate(self.reply)["action"], "BLOCK")

    def test_activity_refreshes_idle_timer(self):
        self.engine.evaluate(self.request)
        self.clock.advance(200)
        self.assertEqual(self.engine.evaluate(self.reply)["action"], "ALLOW")
        self.clock.advance(200)   # 400s since start, 200s since last packet
        self.assertEqual(self.engine.evaluate(self.reply)["action"], "ALLOW")

    def test_packets_without_source_port_stay_stateless(self):
        stateless = Packet("192.168.1.10", "192.168.1.100", 80, "TCP")
        result = self.engine.evaluate(stateless)
        self.assertEqual(result["action"], "ALLOW")
        self.assertIsNone(result["connection_state"])
        self.assertEqual(self.engine.get_statistics()["active_connections"], 0)

    def test_icmp_is_not_tracked(self):
        ping = Packet("192.168.1.10", "192.168.1.100", 0, "ICMP", source_port=0)
        self.engine.evaluate(ping)
        self.assertEqual(self.engine.get_statistics()["active_connections"], 0)

    def test_stateful_can_be_disabled(self):
        self.engine.stateful_enabled = False
        self.engine.evaluate(self.request)
        self.assertEqual(self.engine.evaluate(self.reply)["action"], "BLOCK")

    def test_invalid_source_port_is_blocked(self):
        bad = Packet(
            "192.168.1.10", "192.168.1.100", 80, "TCP", source_port=70000
        )
        result = self.engine.evaluate(bad)
        self.assertEqual(result["action"], "BLOCK")
        self.assertIn("Source port", result["reason"])

    def test_reset_connections(self):
        self.engine.evaluate(self.request)
        self.engine.reset_connections()
        self.assertEqual(self.engine.evaluate(self.reply)["action"], "BLOCK")

    def test_statistics_count_state_decisions(self):
        self.engine.evaluate(self.request)   # allowed by rule
        self.engine.evaluate(self.reply)     # allowed by state
        stats = self.engine.get_statistics()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["allowed"], 2)
        self.assertEqual(stats["active_connections"], 1)

    def test_seconds_remaining_counts_down(self):
        self.engine.evaluate(self.request)
        connection = self.state.get_connections()[0]
        self.assertEqual(self.state.seconds_remaining(connection), 300)
        self.clock.advance(100)
        self.assertEqual(self.state.seconds_remaining(connection), 200)

    def test_old_style_packet_construction_still_works(self):
        p = Packet("10.0.0.5", "8.8.8.8", 80, "TCP")
        self.assertIsNone(p.source_port)
        self.assertEqual(self.engine.evaluate(p)["action"], "BLOCK")


if __name__ == "__main__":
    unittest.main()
