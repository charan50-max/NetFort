import json
import os
import ipaddress
from typing import Optional, Dict, Any, List


DEFAULT_RULES = [
    {
        "rule_id": "RULE-1",
        "name": "Allow Web HTTP",
        "description": "Allow internal client 192.168.1.10 to reach HTTP port 80",
        "source_ip": "192.168.1.10",
        "destination_ip": "*",
        "port": "80",
        "protocol": "TCP",
        "action": "ALLOW",
        "enabled": True
    },
    {
        "rule_id": "RULE-2",
        "name": "Block Telnet Outbound",
        "description": "Prevent insecure Telnet protocol",
        "source_ip": "192.168.1.20",
        "destination_ip": "*",
        "port": "23",
        "protocol": "TCP",
        "action": "BLOCK",
        "enabled": True
    },
    {
        "rule_id": "RULE-3",
        "name": "Allow Outbound HTTPS",
        "description": "Permit standard TLS/HTTPS traffic for all internal clients",
        "source_ip": "*",
        "destination_ip": "*",
        "port": "443",
        "protocol": "TCP",
        "action": "ALLOW",
        "enabled": True
    },
    {
        "rule_id": "RULE-4",
        "name": "Block Rogue Host",
        "description": "Explicitly deny all traffic from rogue host 10.0.0.5",
        "source_ip": "10.0.0.5",
        "destination_ip": "*",
        "port": "*",
        "protocol": "ANY",
        "action": "BLOCK",
        "enabled": True
    },
    {
        "rule_id": "RULE-5",
        "name": "Allow DNS Queries",
        "description": "Permit UDP DNS resolution",
        "source_ip": "*",
        "destination_ip": "*",
        "port": "53",
        "protocol": "UDP",
        "action": "ALLOW",
        "enabled": True
    }
]

PRESETS = {
    "balanced": DEFAULT_RULES,
    "strict": [
        {
            "rule_id": "RULE-1",
            "name": "Allow HTTPS Only",
            "description": "Restrict internal hosts strictly to HTTPS",
            "source_ip": "192.168.1.0/24",
            "destination_ip": "*",
            "port": "443",
            "protocol": "TCP",
            "action": "ALLOW",
            "enabled": True
        },
        {
            "rule_id": "RULE-2",
            "name": "Allow Secure DNS",
            "description": "Permit DNS lookups to internal resolver",
            "source_ip": "192.168.1.0/24",
            "destination_ip": "*",
            "port": "53",
            "protocol": "UDP",
            "action": "ALLOW",
            "enabled": True
        },
        {
            "rule_id": "RULE-3",
            "name": "Block All Inbound Probes",
            "description": "Explicit block on SSH and remote administration",
            "source_ip": "*",
            "destination_ip": "*",
            "port": "22",
            "protocol": "TCP",
            "action": "BLOCK",
            "enabled": True
        }
    ],
    "order_demo": [
        {
            "rule_id": "RULE-1",
            "name": "Broad Allow TCP",
            "description": "Broad allow rule placed before specific block (demonstrates rule shadow)",
            "source_ip": "*",
            "destination_ip": "*",
            "port": "80",
            "protocol": "TCP",
            "action": "ALLOW",
            "enabled": True
        },
        {
            "rule_id": "RULE-2",
            "name": "Specific Deny 192.168.1.50",
            "description": "This rule will be shadowed by Rule #1 because of First-Match-Wins!",
            "source_ip": "192.168.1.50",
            "destination_ip": "*",
            "port": "80",
            "protocol": "TCP",
            "action": "BLOCK",
            "enabled": True
        }
    ]
}


class FirewallRule:
    """
    Represents a single firewall rule.
    """

    def __init__(
        self,
        source_ip="*",
        destination_ip="*",
        port="*",
        protocol="ANY",
        action="BLOCK",
        rule_id=None,
        name=None,
        description=None,
        enabled=True
    ):
        self.source_ip = str(source_ip).strip()
        self.destination_ip = str(destination_ip).strip()
        self.port = str(port).strip()
        self.protocol = str(protocol).upper().strip()
        self.action = str(action).upper().strip()
        self.rule_id = rule_id or "RULE-CUSTOM"
        self.name = name or f"{self.action} {self.protocol} :{self.port}"
        self.description = description or ""
        self.enabled = enabled

    def validate(self):
        """
        Validate the firewall rule.
        """

        # Source IP
        if self.source_ip != "*":
            try:
                if "/" in self.source_ip:
                    ipaddress.ip_network(self.source_ip, strict=False)
                else:
                    ipaddress.ip_address(self.source_ip)
            except ValueError:
                return False, "Invalid source IP."

        # Destination IP
        if self.destination_ip != "*":
            try:
                if "/" in self.destination_ip:
                    ipaddress.ip_network(self.destination_ip, strict=False)
                else:
                    ipaddress.ip_address(self.destination_ip)
            except ValueError:
                return False, "Invalid destination IP."

        # Port
        if self.port != "*":
            try:
                port = int(self.port)

                if port < 0 or port > 65535:
                    return False, "Port must be between 0 and 65535."

            except ValueError:
                return False, "Port must be a number or *."

        # Protocol
        valid_protocols = ["TCP", "UDP", "ICMP", "ANY"]

        if self.protocol not in valid_protocols:
            return False, (
                "Protocol must be TCP, UDP, ICMP or ANY."
            )

        # Action
        if self.action not in ["ALLOW", "BLOCK"]:
            return False, "Action must be ALLOW or BLOCK."

        return True, "Valid rule"

    def _ip_matches(self, pattern: str, target: str) -> bool:
        if pattern == "*":
            return True
        if pattern == target:
            return True
        if "/" in pattern:
            try:
                net = ipaddress.ip_network(pattern, strict=False)
                addr = ipaddress.ip_address(target)
                return addr in net
            except ValueError:
                return False
        return False

    def matches(self, packet):
        """
        Check whether this rule matches a packet.
        """
        if not self.enabled:
            return False

        # Source IP
        if not self._ip_matches(self.source_ip, packet.source_ip):
            return False

        # Destination IP
        if not self._ip_matches(self.destination_ip, packet.destination_ip):
            return False

        # Port
        if self.port != "*":
            if int(self.port) != packet.port:
                return False

        # Protocol
        if self.protocol != "ANY":
            if self.protocol != packet.protocol:
                return False

        return True

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "port": self.port,
            "protocol": self.protocol,
            "action": self.action,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            source_ip=data.get("source_ip", "*"),
            destination_ip=data.get("destination_ip", "*"),
            port=data.get("port", "*"),
            protocol=data.get("protocol", "ANY"),
            action=data.get("action", "BLOCK"),
            rule_id=data.get("rule_id"),
            name=data.get("name"),
            description=data.get("description"),
            enabled=data.get("enabled", True)
        )


class RuleManager:
    """
    Handles loading, saving, adding and deleting rules.
    """

    def __init__(self, file_path="data/rules.json"):
        self.file_path = file_path
        self.rules = []

        self._ensure_directory()
        self.load_rules()

    def _ensure_directory(self):
        directory = os.path.dirname(self.file_path)

        if directory:
            os.makedirs(directory, exist_ok=True)

    def load_rules(self):
        """
        Load rules from JSON.
        """

        try:
            if not os.path.exists(self.file_path):
                self.rules = [
                    FirewallRule.from_dict(rule)
                    for rule in DEFAULT_RULES
                ]

                self.save_rules()
                return

            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            self.rules = []
            for idx, rule in enumerate(data):
                if "rule_id" not in rule:
                    rule["rule_id"] = f"RULE-{idx + 1}"
                self.rules.append(FirewallRule.from_dict(rule))

        except (json.JSONDecodeError, OSError):
            self.rules = [
                FirewallRule.from_dict(rule)
                for rule in DEFAULT_RULES
            ]

            self.save_rules()

    def save_rules(self):
        """
        Save current rules to JSON.
        """

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                [rule.to_dict() for rule in self.rules],
                file,
                indent=4
            )

    def load_preset(self, preset_name: str) -> bool:
        """
        Load a preset ruleset.
        """
        preset = PRESETS.get(preset_name)
        if not preset:
            return False
        self.rules = [FirewallRule.from_dict(r) for r in preset]
        self.save_rules()
        return True

    def reset_to_defaults(self):
        """
        Reset to baseline demo rules.
        """
        self.rules = [FirewallRule.from_dict(r) for r in DEFAULT_RULES]
        self.save_rules()

    def add_rule(self, rule):
        """
        Add a new rule.
        """

        valid, message = rule.validate()

        if not valid:
            return False, message

        if not rule.rule_id or rule.rule_id == "RULE-CUSTOM":
            rule.rule_id = f"RULE-{len(self.rules) + 1}"

        self.rules.append(rule)
        self.save_rules()

        return True, "Rule added successfully."

    def delete_rule(self, index):
        """
        Delete a rule using its zero-based index.
        """

        if index < 0 or index >= len(self.rules):
            return False, "Invalid rule number."

        del self.rules[index]
        self.save_rules()

        return True, "Rule deleted successfully."

    def move_rule_up(self, index):
        """
        Move a rule one position higher.
        """

        if index <= 0 or index >= len(self.rules):
            return False

        self.rules[index], self.rules[index - 1] = (
            self.rules[index - 1],
            self.rules[index]
        )

        self.save_rules()

        return True

    def move_rule_down(self, index):
        """
        Move a rule one position lower.
        """

        if index < 0 or index >= len(self.rules) - 1:
            return False

        self.rules[index], self.rules[index + 1] = (
            self.rules[index + 1],
            self.rules[index]
        )

        self.save_rules()

        return True