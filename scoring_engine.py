from typing import List
from onto_models import OntoTask


def score_risk(task: OntoTask, incident_flags: List[str]) -> int:
    score = 0

    # base risk
    risk_map = {
        "low": 10,
        "medium": 35,
        "high": 65,
        "critical": 85
    }
    score += risk_map.get(task.risk_level, 20)

    # review requirement increases operational sensitivity
    if task.human_review_required:
        score += 10

    # blocked / failed states are higher risk
    if task.result.status == "blocked":
        score += 25
    elif task.result.status == "failed":
        score += 30
    elif task.result.status == "completed":
        score -= 5

    # incident-driven increments
    incident_weights = {
        "policy_block": 20,
        "human_review_missing": 20,
        "failed_execution": 25,
        "inconsistent_parent_child_state": 20,
        "retry_required": 10,
        "replay_gap": 10,
        "low_proof_score": 15,
        "elevated_risk_score": 10,
    }

    for flag in incident_flags:
        score += incident_weights.get(flag, 5)

    return max(0, min(100, score))


def score_trust(task: OntoTask, incident_flags: List[str], proof_score: int) -> int:
    score = 50

    if task.human_approved:
        score += 15

    if task.result.status == "completed":
        score += 20
    elif task.result.status == "failed":
        score -= 20
    elif task.result.status == "blocked":
        score -= 15

    if task.human_review_required and not task.human_approved and task.result.status != "completed":
        score -= 15

    score += int(proof_score * 0.2)
    score -= len(incident_flags) * 8

    return max(0, min(100, score))


def score_proof(
    audit_events_present: bool,
    policy_trace_present: bool,
    approval_trace_present: bool,
    replayable: bool,
    persistence_present: bool,
    reconciliation_trace_present: bool
) -> int:
    score = 0

    if audit_events_present:
        score += 20
    if policy_trace_present:
        score += 20
    if approval_trace_present:
        score += 15
    if replayable:
        score += 20
    if persistence_present:
        score += 15
    if reconciliation_trace_present:
        score += 10

    return max(0, min(100, score))


def compliance_verdict(
    task_status: str,
    risk_score: int,
    trust_score: int,
    proof_score: int,
    incident_flags: List[str]
) -> str:
    if task_status == "blocked":
        return "blocked"

    if task_status == "failed":
        return "failed"

    if "inconsistent_parent_child_state" in incident_flags:
        return "inconsistent"

    if proof_score < 40:
        return "needs_manual_audit"

    if risk_score >= 75:
        return "compliant_with_review"

    if task_status == "completed":
        return "compliant"

    return "needs_manual_audit"