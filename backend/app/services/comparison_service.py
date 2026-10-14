import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from firewall.engine import FirewallEngine
from firewall.rules import RuleManager, FirewallRule
from firewall.state import StatefulFirewall
from backend.app.scenarios import get_scenario_packets


class ComparisonRun:
    def __init__(self, comparison_id: str, scenario_id: str, rules_snapshot: List[FirewallRule]):
        self.comparison_id = comparison_id
        self.scenario_id = scenario_id
        self.created_at = datetime.now().isoformat()

        # Build isolated rule managers with exact same rules snapshot
        temp_mgr_stateless = RuleManager.__new__(RuleManager)
        temp_mgr_stateless.rules = [FirewallRule.from_dict(r.to_dict()) for r in rules_snapshot]

        temp_mgr_stateful = RuleManager.__new__(RuleManager)
        temp_mgr_stateful.rules = [FirewallRule.from_dict(r.to_dict()) for r in rules_snapshot]

        self.stateless_engine = FirewallEngine(
            rule_manager=temp_mgr_stateless,
            stateful_enabled=False
        )

        self.stateful_fw = StatefulFirewall()
        self.stateful_engine = FirewallEngine(
            rule_manager=temp_mgr_stateful,
            stateful_firewall=self.stateful_fw,
            stateful_enabled=True
        )

        self.packets = get_scenario_packets(scenario_id)
        self.results: List[Dict[str, Any]] = []
        self.same_count = 0
        self.diff_count = 0
        self._execute()

    def _execute(self):
        self.results.clear()
        self.same_count = 0
        self.diff_count = 0

        for idx, pkt in enumerate(self.packets):
            res_stateless = self.stateless_engine.evaluate(pkt)
            res_stateful = self.stateful_engine.evaluate(pkt)

            is_diff = (res_stateless["action"] != res_stateful["action"])
            if is_diff:
                self.diff_count += 1
            else:
                self.same_count += 1

            diff_explanation = None
            if is_diff:
                if res_stateful["action"] == "ALLOW" and res_stateless["action"] == "BLOCK":
                    diff_explanation = (
                        "Stateful firewall recognized packet as part of an established bidirectional conversation "
                        f"({res_stateful.get('reason', '')}). Stateless firewall has no session memory and "
                        "blocked it because no explicit inbound rule matches this incoming ephemeral port."
                    )
                elif res_stateful["action"] == "BLOCK" and res_stateless["action"] == "ALLOW":
                    diff_explanation = (
                        "Stateful firewall rejected invalid or unexpected flow, whereas Stateless firewall "
                        "blindly matched an open static rule."
                    )
                else:
                    diff_explanation = f"Stateless: {res_stateless['reason']} | Stateful: {res_stateful['reason']}"

            pair = {
                "sequence": idx + 1,
                "packet_id": pkt.packet_id or f"PKT-{idx + 1:03d}",
                "source_ip": pkt.source_ip,
                "destination_ip": pkt.destination_ip,
                "port": pkt.port,
                "protocol": pkt.protocol,
                "source_port": pkt.source_port,
                "purpose": pkt.purpose or "Simulated Traffic",
                "raw_format": pkt.to_raw_format(),
                "stateless_action": res_stateless["action"],
                "stateless_reason": res_stateless["reason"],
                "stateless_rule": res_stateless.get("matched_rule_name"),
                "stateful_action": res_stateful["action"],
                "stateful_reason": res_stateful["reason"],
                "stateful_rule": res_stateful.get("matched_rule_name"),
                "stateful_connection": res_stateful.get("connection_state"),
                "is_difference": is_diff,
                "difference_explanation": diff_explanation
            }
            self.results.append(pair)

    def to_dict(self) -> Dict[str, Any]:
        total = len(self.packets)
        stateless_stats = self.stateless_engine.get_statistics()
        stateful_stats = self.stateful_engine.get_statistics()
        disagreement_rate = round((self.diff_count / total * 100), 2) if total > 0 else 0.0

        return {
            "comparison_id": self.comparison_id,
            "scenario_id": self.scenario_id,
            "total_packets": total,
            "same_count": self.same_count,
            "diff_count": self.diff_count,
            "disagreement_rate": disagreement_rate,
            "stateless_allowed": stateless_stats["allowed"],
            "stateless_blocked": stateless_stats["blocked"],
            "stateful_allowed": stateful_stats["allowed"],
            "stateful_blocked": stateful_stats["blocked"],
            "results": self.results
        }


class ComparisonService:
    def __init__(self, rule_manager: RuleManager):
        self.rule_manager = rule_manager
        self.comparisons: Dict[str, ComparisonRun] = {}
        self.latest_comparison_id: Optional[str] = None

    def run_comparison(self, scenario_id: str = "enterprise_100") -> ComparisonRun:
        comp_id = f"cmp-{uuid.uuid4().hex[:8]}"
        comp = ComparisonRun(
            comparison_id=comp_id,
            scenario_id=scenario_id,
            rules_snapshot=self.rule_manager.rules
        )
        self.comparisons[comp_id] = comp
        self.latest_comparison_id = comp_id
        return comp

    def get_comparison(self, comp_id: str) -> Optional[ComparisonRun]:
        return self.comparisons.get(comp_id)

    def get_latest(self) -> Optional[ComparisonRun]:
        if not self.latest_comparison_id:
            return None
        return self.comparisons.get(self.latest_comparison_id)
