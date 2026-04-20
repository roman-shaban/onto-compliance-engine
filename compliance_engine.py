import json
import os
from datetime import datetime
from typing import List, Dict

from onto_models import OntoTask
from compliance_models import ComplianceEvent, ComplianceRecord, ProofRecord
from scoring_engine import score_risk, score_trust, score_proof, compliance_verdict


STORAGE_DIR = "storage"
TASKS_FILE = os.path.join(STORAGE_DIR, "tasks.json")
AUDIT_FILE = "audit_log.json"
COMPLIANCE_FILE = os.path.join(STORAGE_DIR, "compliance_records.json")


def _load_json(path: str):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _load_audit_lines() -> List[dict]:
    if not os.path.exists(AUDIT_FILE):
        return []

    records = []
    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _task_has_persistence(task_id: str) -> bool:
    tasks = _load_json(TASKS_FILE)
    return task_id in tasks


def _get_task_audit_events(task_id: str) -> List[dict]:
    return [row for row in _load_audit_lines() if row.get("task_id") == task_id]


def _get_run_tasks(run_id: str) -> List[dict]:
    tasks = _load_json(TASKS_FILE)
    return [task for task in tasks.values() if task.get("run_id") == run_id]


def _detect_incidents(task: OntoTask, proof_score_value: int) -> List[str]:
    incidents = []

    if task.result.status == "blocked":
        incidents.append("policy_block")

    if task.result.status == "failed":
        incidents.append("failed_execution")

    if task.human_review_required and not task.human_approved and task.result.status != "completed":
        incidents.append("human_review_missing")

    if proof_score_value < 40:
        incidents.append("low_proof_score")

    return incidents


def _build_proof_record(task: OntoTask) -> ProofRecord:
    audit_events = _get_task_audit_events(task.task_id)

    audit_events_present = len(audit_events) > 0
    policy_trace_present = any(
        row.get("decision") in ["allowed", "blocked", "failed", "started", "delegated", "received"]
        for row in audit_events
    )
    approval_trace_present = task.human_approved
    replayable = _task_has_persistence(task.task_id)
    persistence_present = _task_has_persistence(task.task_id)

    reconciliation_trace_present = any(
        "recon" in str(row.get("event_type", "")).lower()
        or "recon" in str(row.get("reason", "")).lower()
        for row in audit_events
    )

    proof_score_value = score_proof(
        audit_events_present=audit_events_present,
        policy_trace_present=policy_trace_present,
        approval_trace_present=approval_trace_present,
        replayable=replayable,
        persistence_present=persistence_present,
        reconciliation_trace_present=reconciliation_trace_present,
    )

    if proof_score_value >= 80:
        proof_status = "strong"
        confidence_level = "high"
    elif proof_score_value >= 50:
        proof_status = "moderate"
        confidence_level = "medium"
    else:
        proof_status = "weak"
        confidence_level = "low"

    return ProofRecord(
        proof_status=proof_status,
        sources_present=False,
        tools_recorded=False,
        execution_trace_present=audit_events_present,
        policy_trace_present=policy_trace_present,
        approval_trace_present=approval_trace_present,
        replayable=replayable,
        confidence_level=confidence_level,
        proof_score=proof_score_value,
    )


def evaluate_task_compliance(task: OntoTask) -> ComplianceRecord:
    proof = _build_proof_record(task)
    incident_flags = _detect_incidents(task, proof.proof_score)

    risk_score = score_risk(task, incident_flags)
    trust_score = score_trust(task, incident_flags, proof.proof_score)

    final_verdict = compliance_verdict(
        task_status=task.result.status,
        risk_score=risk_score,
        trust_score=trust_score,
        proof_score=proof.proof_score,
        incident_flags=incident_flags,
    )

    if task.result.status == "completed":
        compliance_status = "clean"
    elif task.result.status == "blocked":
        compliance_status = "blocked"
    elif task.result.status == "failed":
        compliance_status = "failed"
    else:
        compliance_status = "open"

    review_status = "approved" if task.human_approved else (
        "required" if task.human_review_required else "not_required"
    )

    return ComplianceRecord(
        run_id=task.run_id,
        task_id=task.task_id,
        parent_task_id=task.parent_task_id,
        agent_name=task.agent.name,
        intent_action=task.intent.action,
        compliance_status=compliance_status,
        risk_score=risk_score,
        trust_score=trust_score,
        proof_score=proof.proof_score,
        review_status=review_status,
        incident_flags=incident_flags,
        final_verdict=final_verdict,
        notes="Generated by AI Compliance + Scoring Engine v1",
        task_status=task.result.status,
        task_output=task.result.output,
        proof=proof,
    )


def save_compliance_record(record: ComplianceRecord):
    data = _load_json(COMPLIANCE_FILE)

    # Один task = один запис.
    # Якщо той самий task зберігається ще раз, запис оновлюється, а не дублюється.
    data[record.task_id] = record.model_dump()

    _save_json(COMPLIANCE_FILE, data)


def emit_compliance_event(task: OntoTask, event_type: str, policy_decision: str = None, policy_summary: str = None):
    event = ComplianceEvent(
        timestamp=datetime.utcnow().isoformat(),
        run_id=task.run_id,
        task_id=task.task_id,
        parent_task_id=task.parent_task_id,
        agent_name=task.agent.name,
        intent_action=task.intent.action,
        event_type=event_type,
        policy_decision=policy_decision,
        policy_summary=policy_summary,
        human_review_required=task.human_review_required,
        human_approved=task.human_approved,
        risk_level=task.risk_level,
        result_status=task.result.status,
        result_output=task.result.output,
        compliance_severity="medium" if task.risk_level == "medium" else "low",
        evidence_refs=[],
    )
    return event


def summarize_run_compliance(run_id: str) -> Dict:
    tasks = _get_run_tasks(run_id)

    task_count = len(tasks)
    blocked_count = sum(1 for t in tasks if t.get("status") == "blocked")
    failed_count = sum(1 for t in tasks if t.get("status") == "failed")
    completed_count = sum(1 for t in tasks if t.get("status") == "completed")

    high_risk_task_count = sum(
        1 for t in tasks if t.get("risk_level") in ["high", "critical"]
    )

    incidents = []
    for task in tasks:
        if task.get("status") == "blocked":
            incidents.append({
                "task_id": task.get("task_id"),
                "incident": "policy_block"
            })
        if task.get("status") == "failed":
            incidents.append({
                "task_id": task.get("task_id"),
                "incident": "failed_execution"
            })

    if failed_count > 0:
        overall_verdict = "failed"
    elif blocked_count > 0:
        overall_verdict = "blocked"
    elif completed_count == task_count and task_count > 0:
        overall_verdict = "compliant"
    else:
        overall_verdict = "needs_manual_audit"

    return {
        "run_id": run_id,
        "task_count": task_count,
        "blocked_count": blocked_count,
        "failed_count": failed_count,
        "completed_count": completed_count,
        "high_risk_task_count": high_risk_task_count,
        "incidents": incidents,
        "overall_verdict": overall_verdict,
    }