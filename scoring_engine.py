# Copyright (c) 2026 Roman Shaban. All rights reserved.
# Licensed under the Apache License 2.0.
# Part of the CIOS / Onto-Protocol Ecosystem.

from typing import List
from onto_models import OntoTask

def score_risk(task: OntoTask, incident_flags: List[str]) -> int:
    """
    CIOS Risk Assessment Model v2.1
    Combines baseline severity with non-linear incident accumulation.
    """
    # 1. Base Severity (from original risk_map)
    risk_map = {
        "low": 10,
        "medium": 35,
        "high": 65,
        "critical": 85
    }
    score = risk_map.get(task.risk_level, 20)

    # 2. Operational Sensitivity
    if task.human_review_required:
        score += 10

    # 3. Execution State Adjustments
    if task.result.status == "blocked":
        score += 25
    elif task.result.status == "failed":
        score += 30
    elif task.result.status == "completed":
        score -= 5

    # 4. Incident-driven increments (Non-linear accumulation)
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

    incident_impact = 0
    multiplier = 1.0 # Every incident makes the next one more severe
    for flag in incident_flags:
        impact = incident_weights.get(flag, 5)
        incident_impact += (impact * multiplier)
        multiplier *= 1.15 # 15% increase per incident

    score += int(incident_impact)
    return max(0, min(100, score))


def score_trust(task: OntoTask, incident_flags: List[str], proof_score: int) -> int:
    """
    Probabilistic Trust Model v2.1
    Evaluates agent reliability using Bayesian-like evidence weighting.
    """
    # Start with baseline
    score = 50

    # 1. Success Bonus
    if task.human_approved:
        score += 15

    if task.result.status == "completed":
        score += 20
    elif task.result.status == "failed":
        score -= 20
    elif task.result.status == "blocked":
        score -= 15

    # Penalty for ignoring review requirements
    if task.human_review_required and not task.human_approved and task.result.status != "completed":
        score -= 15

    # 2. Penalty (Exponential impact of incidents)
    penalty_base = 8 # Base penalty from original code
    penalty_total = 0
    for _ in incident_flags:
        penalty_total += penalty_base
        penalty_base *= 1.2  # Every subsequent incident is more damaging
    
    score -= int(penalty_total)

    # 3. Proof Integration (Trust is limited by available evidence)
    # Even a successful agent cannot have 100% trust without solid proof
    proof_normalized = proof_score / 100.0
    final_score = score * (0.6 + 0.4 * proof_normalized)

    return int(max(0, min(100, final_score)))


def score_proof(
    audit_events_present: bool,
    policy_trace_present: bool,
    approval_trace_present: bool,
    replayable: bool,
    persistence_present: bool,
    reconciliation_trace_present: bool
) -> int:
    """
    Deterministic Evidence Weighting
    Calculates the 'Proof Density' of the execution trace.
    """
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
    """
    Logic Gate for Final System Verdict
    """
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
