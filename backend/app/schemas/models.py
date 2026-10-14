from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RuleSchema(BaseModel):
    rule_id: str
    name: str
    description: Optional[str] = ""
    source_ip: str = "*"
    destination_ip: str = "*"
    port: str = "*"
    protocol: str = "ANY"
    action: str = "BLOCK"
    enabled: bool = True


class RuleCreateSchema(BaseModel):
    name: str
    description: Optional[str] = ""
    source_ip: str = "*"
    destination_ip: str = "*"
    port: str = "*"
    protocol: str = "ANY"
    action: str = "BLOCK"
    enabled: bool = True


class RuleUpdateListSchema(BaseModel):
    rules: List[RuleSchema]


class PacketSchema(BaseModel):
    packet_id: str
    sequence: int
    source_ip: str
    destination_ip: str
    port: int
    protocol: str
    source_port: Optional[int] = None
    purpose: str
    explanation: Optional[str] = ""
    flow_id: Optional[str] = ""
    direction: Optional[str] = "OUTBOUND"
    payload_summary: Optional[str] = ""
    tcp_flags: Optional[str] = None
    raw_format: Optional[str] = None


class ScenarioInfo(BaseModel):
    id: str
    name: str
    description: str
    packet_count: int
    recommended: bool


class EvaluationResultSchema(BaseModel):
    packet_id: Optional[str] = None
    action: str
    matched_rule: Optional[int] = None
    matched_rule_id: Optional[str] = None
    matched_rule_name: Optional[str] = None
    reason_code: str
    reason: str
    connection_state: Optional[str] = None
    processing_time_ms: float
    packet: Optional[PacketSchema] = None


class SimulationCreateRequest(BaseModel):
    scenario_id: str = "enterprise_100"
    model_type: str = "stateful"  # "stateful" or "stateless"


class SimulationSummary(BaseModel):
    run_id: str
    scenario_id: str
    scenario_name: str
    model_type: str
    status: str  # "ready", "running", "paused", "completed", "stopped"
    total_packets: int
    processed_packets: int
    allowed_count: int
    blocked_count: int
    allow_rate: float
    block_rate: float
    active_connections: int
    current_packet_index: int
    created_at: str
    completed_at: Optional[str] = None
    latest_result: Optional[EvaluationResultSchema] = None


class SimulationStepResponse(BaseModel):
    status: str
    processed_packets: int
    total_packets: int
    finished: bool
    step_result: Optional[EvaluationResultSchema] = None
    summary: SimulationSummary


class ComparisonResultPair(BaseModel):
    sequence: int
    packet_id: str
    source_ip: str
    destination_ip: str
    port: int
    protocol: str
    source_port: Optional[int] = None
    purpose: str
    raw_format: str
    stateless_action: str
    stateless_reason: str
    stateless_rule: Optional[str] = None
    stateful_action: str
    stateful_reason: str
    stateful_rule: Optional[str] = None
    stateful_connection: Optional[str] = None
    is_difference: bool
    difference_explanation: Optional[str] = None


class ComparisonResponse(BaseModel):
    comparison_id: str
    scenario_id: str
    total_packets: int
    same_count: int
    diff_count: int
    disagreement_rate: float
    stateless_allowed: int
    stateless_blocked: int
    stateful_allowed: int
    stateful_blocked: int
    results: List[ComparisonResultPair]


class MetricsSummary(BaseModel):
    run_id: str
    total_packets: int
    allowed_count: int
    blocked_count: int
    allow_rate: float
    block_rate: float
    invalid_packets: int
    default_blocks: int
    rule_allows: int
    rule_blocks: int
    stateful_allows: int
    active_connections: int
    average_latency_ms: float
    total_runtime_ms: float
    is_comparison: bool = False
    comparison_metrics: Optional[Dict[str, Any]] = None
