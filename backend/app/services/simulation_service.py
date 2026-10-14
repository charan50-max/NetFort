import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from firewall.engine import FirewallEngine
from firewall.rules import RuleManager, FirewallRule
from firewall.state import StatefulFirewall
from backend.app.scenarios import get_scenario_packets, SCENARIOS


class SimulationRun:
    def __init__(self, run_id: str, scenario_id: str, model_type: str, rules_snapshot: List[FirewallRule]):
        self.run_id = run_id
        self.scenario_id = scenario_id
        self.scenario_name = SCENARIOS.get(scenario_id, {}).get("name", "Custom Stream")
        self.model_type = model_type.lower()
        self.status = "ready"
        self.created_at = datetime.now().isoformat()
        self.completed_at = None

        # Build dedicated rules manager for this run snapshot
        temp_manager = RuleManager.__new__(RuleManager)
        temp_manager.rules = [FirewallRule.from_dict(r.to_dict()) for r in rules_snapshot]
        self.rules = temp_manager.rules

        # Create isolated engine
        self.stateful_fw = StatefulFirewall()
        self.engine = FirewallEngine(
            rule_manager=temp_manager,
            stateful_firewall=self.stateful_fw,
            stateful_enabled=(self.model_type == "stateful")
        )

        # Load 100 packets
        self.packets = get_scenario_packets(scenario_id)
        self.total_packets = len(self.packets)
        self.current_index = 0
        self.evaluated_packets = []
        self.total_eval_time_ms = 0.0
        self.latest_result = None

    def step(self, batch_size: int = 1) -> Optional[Dict[str, Any]]:
        if self.status in ("completed", "stopped"):
            return None

        self.status = "running"
        last_result = None

        for _ in range(batch_size):
            if self.current_index >= self.total_packets:
                self.status = "completed"
                self.completed_at = datetime.now().isoformat()
                break

            pkt = self.packets[self.current_index]
            eval_res = self.engine.evaluate(pkt)
            self.total_eval_time_ms += eval_res.get("processing_time_ms", 0.0)

            # Store full packet information along with outcome
            record = {
                "sequence": self.current_index + 1,
                "packet_id": pkt.packet_id or f"PKT-{self.current_index + 1:03d}",
                "packet": pkt.to_dict(),
                "action": eval_res["action"],
                "matched_rule": eval_res["matched_rule"],
                "matched_rule_id": eval_res.get("matched_rule_id"),
                "matched_rule_name": eval_res.get("matched_rule_name"),
                "reason_code": eval_res.get("reason_code", "UNKNOWN"),
                "reason": eval_res["reason"],
                "connection_state": eval_res.get("connection_state"),
                "processing_time_ms": eval_res.get("processing_time_ms", 0.0),
                "timestamp": datetime.now().isoformat()
            }
            self.evaluated_packets.append(record)
            self.current_index += 1
            last_result = record

        if self.current_index >= self.total_packets and self.status != "stopped":
            self.status = "completed"
            self.completed_at = datetime.now().isoformat()

        self.latest_result = last_result
        return last_result

    def pause(self):
        if self.status == "running":
            self.status = "paused"

    def resume(self):
        if self.status == "paused":
            self.status = "running"

    def stop(self):
        self.status = "stopped"
        self.completed_at = datetime.now().isoformat()

    def restart(self):
        self.status = "ready"
        self.current_index = 0
        self.evaluated_packets.clear()
        self.engine.reset_statistics()
        self.engine.reset_connections()
        self.total_eval_time_ms = 0.0
        self.latest_result = None
        self.completed_at = None

    def get_summary(self) -> Dict[str, Any]:
        stats = self.engine.get_statistics()
        return {
            "run_id": self.run_id,
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "model_type": self.model_type,
            "status": self.status,
            "total_packets": self.total_packets,
            "processed_packets": len(self.evaluated_packets),
            "allowed_count": stats["allowed"],
            "blocked_count": stats["blocked"],
            "allow_rate": stats["allow_rate"],
            "block_rate": stats["block_rate"],
            "active_connections": stats["active_connections"],
            "current_packet_index": self.current_index,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "latest_result": self.latest_result
        }


class SimulationService:
    def __init__(self, rule_manager: RuleManager):
        self.rule_manager = rule_manager
        self.runs: Dict[str, SimulationRun] = {}
        self.recent_run_ids: List[str] = []

    def create_simulation(self, scenario_id: str = "enterprise_100", model_type: str = "stateful") -> SimulationRun:
        run_id = f"sim-{uuid.uuid4().hex[:8]}"
        run = SimulationRun(
            run_id=run_id,
            scenario_id=scenario_id,
            model_type=model_type,
            rules_snapshot=self.rule_manager.rules
        )
        self.runs[run_id] = run
        self.recent_run_ids.insert(0, run_id)
        if len(self.recent_run_ids) > 20:
            self.recent_run_ids = self.recent_run_ids[:20]
        return run

    def get_simulation(self, run_id: str) -> Optional[SimulationRun]:
        return self.runs.get(run_id)

    def get_latest_simulation(self) -> Optional[SimulationRun]:
        if not self.recent_run_ids:
            return None
        return self.runs.get(self.recent_run_ids[0])

    def get_all_summaries(self) -> List[Dict[str, Any]]:
        return [self.runs[rid].get_summary() for rid in self.recent_run_ids if rid in self.runs]

    def get_packets(
        self,
        run_id: str,
        page: int = 1,
        limit: int = 50,
        filter_outcome: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        run = self.get_simulation(run_id)
        if not run:
            return {"total": 0, "packets": [], "page": page, "limit": limit}

        records = run.evaluated_packets

        if filter_outcome and filter_outcome.upper() in ("ALLOW", "BLOCK"):
            records = [r for r in records if r["action"] == filter_outcome.upper()]

        if search:
            query = search.strip().lower()
            records = [
                r for r in records
                if (
                    query in r["packet_id"].lower()
                    or query in r["packet"]["source_ip"].lower()
                    or query in r["packet"]["destination_ip"].lower()
                    or query in str(r["packet"]["port"])
                    or query in r["packet"]["protocol"].lower()
                    or query in r["reason"].lower()
                    or query in r["packet"].get("purpose", "").lower()
                )
            ]

        total = len(records)
        start = (page - 1) * limit
        end = start + limit
        paged_packets = records[start:end]

        return {
            "total": total,
            "packets": paged_packets,
            "page": page,
            "limit": limit
        }
