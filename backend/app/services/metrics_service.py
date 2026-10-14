from typing import Dict, Any, Optional
from backend.app.services.simulation_service import SimulationRun
from backend.app.services.comparison_service import ComparisonRun


class MetricsService:
    @staticmethod
    def compute_simulation_metrics(run: SimulationRun) -> Dict[str, Any]:
        stats = run.engine.get_statistics()
        total = stats["total"]
        avg_latency = round(run.total_eval_time_ms / total, 3) if total > 0 else 0.0

        return {
            "run_id": run.run_id,
            "scenario_id": run.scenario_id,
            "scenario_name": run.scenario_name,
            "model_type": run.model_type,
            "status": run.status,
            "total_packets": total,
            "allowed_count": stats["allowed"],
            "blocked_count": stats["blocked"],
            "allow_rate": stats["allow_rate"],
            "block_rate": stats["block_rate"],
            "invalid_packets": stats["invalid_packets"],
            "default_blocks": stats["default_blocks"],
            "rule_allows": stats["rule_allows"],
            "rule_blocks": stats["rule_blocks"],
            "stateful_allows": stats["stateful_allows"],
            "active_connections": stats["active_connections"],
            "average_latency_ms": avg_latency,
            "total_runtime_ms": round(run.total_eval_time_ms, 2),
            "is_comparison": False,
            "comparison_metrics": None
        }

    @staticmethod
    def compute_comparison_metrics(comp: ComparisonRun) -> Dict[str, Any]:
        total = len(comp.packets)
        stateless_stats = comp.stateless_engine.get_statistics()
        stateful_stats = comp.stateful_engine.get_statistics()

        differing_packet_ids = [
            pair["packet_id"] for pair in comp.results if pair["is_difference"]
        ]
        disagreement_rate = round((comp.diff_count / total * 100), 2) if total > 0 else 0.0

        return {
            "run_id": comp.comparison_id,
            "scenario_id": comp.scenario_id,
            "scenario_name": f"Comparison: {comp.scenario_id}",
            "model_type": "comparison",
            "status": "completed",
            "total_packets": total,
            "allowed_count": stateful_stats["allowed"],
            "blocked_count": stateful_stats["blocked"],
            "allow_rate": stateful_stats["allow_rate"],
            "block_rate": stateful_stats["block_rate"],
            "invalid_packets": stateful_stats["invalid_packets"],
            "default_blocks": stateful_stats["default_blocks"],
            "rule_allows": stateful_stats["rule_allows"],
            "rule_blocks": stateful_stats["rule_blocks"],
            "stateful_allows": stateful_stats["stateful_allows"],
            "active_connections": stateful_stats["active_connections"],
            "average_latency_ms": 0.05,
            "total_runtime_ms": 5.0,
            "is_comparison": True,
            "comparison_metrics": {
                "disagreement_rate": disagreement_rate,
                "diff_count": comp.diff_count,
                "same_count": comp.same_count,
                "differing_packet_ids": differing_packet_ids,
                "stateless": {
                    "allowed": stateless_stats["allowed"],
                    "blocked": stateless_stats["blocked"],
                    "allow_rate": stateless_stats["allow_rate"],
                    "block_rate": stateless_stats["block_rate"],
                },
                "stateful": {
                    "allowed": stateful_stats["allowed"],
                    "blocked": stateful_stats["blocked"],
                    "allow_rate": stateful_stats["allow_rate"],
                    "block_rate": stateful_stats["block_rate"],
                    "active_connections": stateful_stats["active_connections"]
                }
            }
        }
