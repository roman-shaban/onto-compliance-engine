from pydantic import BaseModel, Field
from typing import List, Optional
import uuid


class ComplianceEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str

    run_id: Optional[str] = None
    task_id: str
    parent_task_id: Optional[str] = None

    agent_name: str
    intent_action: str
    event_type: str

    policy_decision: Optional[str] = None
    policy_summary: Optional[str] = None

    human_review_required: bool = False
    human_approved: bool = False

    risk_level: str = "low"
    result_status: str = "pending"
    result_output: Optional[str] = None

    compliance_severity: str = "low"
    evidence_refs: List[str] = Field(default_factory=list)


class ProofRecord(BaseModel):
    proof_status: str
    sources_present: bool
    tools_recorded: bool
    execution_trace_present: bool
    policy_trace_present: bool
    approval_trace_present: bool
    replayable: bool
    confidence_level: str
    proof_score: int


class ComplianceRecord(BaseModel):
    compliance_record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    run_id: Optional[str] = None
    task_id: str
    parent_task_id: Optional[str] = None

    agent_name: str
    intent_action: str

    compliance_status: str
    risk_score: int
    trust_score: int
    proof_score: int

    review_status: str
    incident_flags: List[str] = Field(default_factory=list)
    final_verdict: str
    notes: Optional[str] = None

    task_status: str
    task_output: Optional[str] = None

    proof: ProofRecord