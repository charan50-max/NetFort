import csv
import io
from fastapi import APIRouter, HTTPException, Query, Response
from typing import Optional, List, Dict, Any
from firewall.rules import RuleManager, FirewallRule
from backend.app.scenarios import SCENARIOS, get_scenario_packets
from backend.app.schemas.models import (
    RuleSchema, RuleCreateSchema, RuleUpdateListSchema, ScenarioInfo,
    SimulationCreateRequest, SimulationSummary, SimulationStepResponse,
    ComparisonResponse, MetricsSummary
)
from backend.app.services.simulation_service import SimulationService
from backend.app.services.comparison_service import ComparisonService
from backend.app.services.metrics_service import MetricsService

router = APIRouter()

# Global instances initialized with project rule manager
rule_manager = RuleManager("data/rules.json")
simulation_service = SimulationService(rule_manager)
comparison_service = ComparisonService(rule_manager)


# ---- Health ----
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": "NetFort Web Firewall Simulator",
        "version": "2.0.0",
        "packets_per_scenario": 100
    }


# ---- Scenarios ----
@router.get("/scenarios", response_model=List[ScenarioInfo])
def list_scenarios():
    return [
        ScenarioInfo(
            id=s["id"],
            name=s["name"],
            description=s["description"],
            packet_count=s["packet_count"],
            recommended=s["recommended"]
        )
        for s in SCENARIOS.values()
    ]


@router.get("/scenarios/{scenario_id}/packets")
def get_scenario_packet_list(scenario_id: str):
    if scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    pkts = get_scenario_packets(scenario_id)
    return [p.to_dict() for p in pkts]


# ---- Rules ----
@router.get("/rules", response_model=List[RuleSchema])
def get_rules():
    return [
        RuleSchema(
            rule_id=getattr(r, "rule_id", f"RULE-{i+1}"),
            name=getattr(r, "name", f"Rule #{i+1}"),
            description=getattr(r, "description", ""),
            source_ip=r.source_ip,
            destination_ip=r.destination_ip,
            port=r.port,
            protocol=r.protocol,
            action=r.action,
            enabled=getattr(r, "enabled", True)
        )
        for i, r in enumerate(rule_manager.rules)
    ]


@router.put("/rules")
def update_rules(payload: RuleUpdateListSchema):
    new_rules = []
    for item in payload.rules:
        rule = FirewallRule(
            source_ip=item.source_ip,
            destination_ip=item.destination_ip,
            port=item.port,
            protocol=item.protocol,
            action=item.action,
            rule_id=item.rule_id,
            name=item.name,
            description=item.description,
            enabled=item.enabled
        )
        valid, msg = rule.validate()
        if not valid:
            raise HTTPException(status_code=400, detail=f"Invalid rule '{item.name}': {msg}")
        new_rules.append(rule)

    rule_manager.rules = new_rules
    rule_manager.save_rules()
    return {"message": "Rules updated successfully.", "count": len(new_rules)}


@router.post("/rules")
def add_rule(item: RuleCreateSchema):
    rule = FirewallRule(
        source_ip=item.source_ip,
        destination_ip=item.destination_ip,
        port=item.port,
        protocol=item.protocol,
        action=item.action,
        rule_id=f"RULE-{len(rule_manager.rules) + 1}",
        name=item.name,
        description=item.description,
        enabled=item.enabled
    )
    ok, msg = rule_manager.add_rule(rule)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": "Rule added.", "rule": rule.to_dict()}


@router.delete("/rules/{index}")
def delete_rule(index: int):
    ok, msg = rule_manager.delete_rule(index)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@router.post("/rules/move-up/{index}")
def move_rule_up(index: int):
    if not rule_manager.move_rule_up(index):
        raise HTTPException(status_code=400, detail="Cannot move rule up.")
    return {"message": "Rule moved up."}


@router.post("/rules/move-down/{index}")
def move_rule_down(index: int):
    if not rule_manager.move_rule_down(index):
        raise HTTPException(status_code=400, detail="Cannot move rule down.")
    return {"message": "Rule moved down."}


@router.post("/rules/reset")
def reset_rules():
    rule_manager.reset_to_defaults()
    return {"message": "Rules reset to default demo rules.", "count": len(rule_manager.rules)}


@router.post("/rules/presets/{preset_name}")
def apply_preset(preset_name: str):
    if not rule_manager.load_preset(preset_name):
        raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found.")
    return {"message": f"Preset '{preset_name}' applied successfully."}


# ---- Simulations ----
@router.post("/simulations", response_model=SimulationSummary)
def create_simulation(payload: SimulationCreateRequest):
    if payload.scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{payload.scenario_id}' not found.")
    run = simulation_service.create_simulation(
        scenario_id=payload.scenario_id,
        model_type=payload.model_type
    )
    return run.get_summary()


@router.get("/simulations/latest")
def get_latest_simulation():
    run = simulation_service.get_latest_simulation()
    if not run:
        # Create a default run if none exists yet
        run = simulation_service.create_simulation("enterprise_100", "stateful")
    return run.get_summary()


@router.get("/simulations/history")
def get_simulation_history():
    return simulation_service.get_all_summaries()


@router.get("/simulations/{run_id}", response_model=SimulationSummary)
def get_simulation(run_id: str):
    run = simulation_service.get_simulation(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")
    return run.get_summary()


@router.post("/simulations/{run_id}/step", response_model=SimulationStepResponse)
def step_simulation(run_id: str, batch_size: int = Query(1, ge=1, le=100)):
    run = simulation_service.get_simulation(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")

    res = run.step(batch_size=batch_size)
    summary = run.get_summary()
    return SimulationStepResponse(
        status=run.status,
        processed_packets=len(run.evaluated_packets),
        total_packets=run.total_packets,
        finished=(run.current_index >= run.total_packets),
        step_result=res,
        summary=summary
    )


@router.post("/simulations/{run_id}/pause")
def pause_simulation(run_id: str):
    run = simulation_service.get_simulation(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")
    run.pause()
    return run.get_summary()


@router.post("/simulations/{run_id}/resume")
def resume_simulation(run_id: str):
    run = simulation_service.get_simulation(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")
    run.resume()
    return run.get_summary()


@router.post("/simulations/{run_id}/stop")
def stop_simulation(run_id: str):
    run = simulation_service.get_simulation(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")
    run.stop()
    return run.get_summary()


@router.post("/simulations/{run_id}/restart")
def restart_simulation(run_id: str):
    run = simulation_service.get_simulation(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")
    run.restart()
    return run.get_summary()


@router.get("/simulations/{run_id}/packets")
def get_simulation_packets(
    run_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    filter_outcome: Optional[str] = None,
    search: Optional[str] = None
):
    return simulation_service.get_packets(
        run_id=run_id,
        page=page,
        limit=limit,
        filter_outcome=filter_outcome,
        search=search
    )


# ---- Comparisons ----
@router.post("/comparisons", response_model=ComparisonResponse)
def create_comparison(scenario_id: str = Query("enterprise_100")):
    if scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    comp = comparison_service.run_comparison(scenario_id=scenario_id)
    return comp.to_dict()


@router.get("/comparisons/latest", response_model=ComparisonResponse)
def get_latest_comparison():
    comp = comparison_service.get_latest()
    if not comp:
        comp = comparison_service.run_comparison("enterprise_100")
    return comp.to_dict()


@router.get("/comparisons/{comp_id}", response_model=ComparisonResponse)
def get_comparison(comp_id: str):
    comp = comparison_service.get_comparison(comp_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Comparison run not found.")
    return comp.to_dict()


# ---- Metrics ----
@router.get("/metrics/{run_id}")
def get_metrics(run_id: str):
    # Check if run_id is a comparison
    if run_id.startswith("cmp-"):
        comp = comparison_service.get_comparison(run_id)
        if not comp:
            raise HTTPException(status_code=404, detail="Comparison not found.")
        return MetricsService.compute_comparison_metrics(comp)

    # Check simulation run
    run = simulation_service.get_simulation(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found.")
    return MetricsService.compute_simulation_metrics(run)


@router.get("/metrics/latest/view")
def get_latest_metrics():
    # If a comparison exists, prefer comparison metrics; otherwise simulation metrics
    comp = comparison_service.get_latest()
    if comp:
        return MetricsService.compute_comparison_metrics(comp)

    run = simulation_service.get_latest_simulation()
    if run:
        return MetricsService.compute_simulation_metrics(run)

    # If nothing has run yet, run a comparison to populate rich metrics
    comp = comparison_service.run_comparison("enterprise_100")
    return MetricsService.compute_comparison_metrics(comp)


# ---- Export CSV ----
@router.get("/export/{run_id}/csv")
def export_csv(run_id: str):
    output = io.StringIO()
    writer = csv.writer(output)

    if run_id.startswith("cmp-"):
        comp = comparison_service.get_comparison(run_id)
        if not comp:
            raise HTTPException(status_code=404, detail="Comparison not found.")
        writer.writerow([
            "Sequence", "Packet ID", "Source IP", "Source Port", "Destination IP",
            "Destination Port", "Protocol", "Purpose", "Stateless Decision",
            "Stateful Decision", "Difference?", "Explanation"
        ])
        for p in comp.results:
            writer.writerow([
                p["sequence"], p["packet_id"], p["source_ip"], p["source_port"],
                p["destination_ip"], p["port"], p["protocol"], p["purpose"],
                p["stateless_action"], p["stateful_action"],
                "YES" if p["is_difference"] else "NO",
                p["difference_explanation"] or ""
            ])
        filename = f"netfort-comparison-{run_id}.csv"
    else:
        run = simulation_service.get_simulation(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Simulation not found.")
        writer.writerow([
            "Sequence", "Packet ID", "Source IP", "Source Port", "Destination IP",
            "Destination Port", "Protocol", "Purpose", "Action", "Matched Rule",
            "Reason Code", "Reason", "Connection State"
        ])
        for p in run.evaluated_packets:
            writer.writerow([
                p["sequence"], p["packet_id"], p["packet"]["source_ip"],
                p["packet"]["source_port"], p["packet"]["destination_ip"],
                p["packet"]["port"], p["packet"]["protocol"], p["packet"]["purpose"],
                p["action"], p["matched_rule_name"] or "", p["reason_code"],
                p["reason"], p["connection_state"] or ""
            ])
        filename = f"netfort-simulation-{run_id}.csv"

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
