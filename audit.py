# Copyright (c) 2026 Roman Shaban. All rights reserved.
# Licensed under the Apache License 2.0.
# Part of the CIOS / Onto-Protocol Ecosystem.
import json
from datetime import datetime, timezone
from onto_models import OntoTask


def log_event(task: OntoTask, event_type: str, decision: str, reason: str):
    timestamp_utc = datetime.now(timezone.utc).isoformat()

    task_role = "child" if task.parent_task_id else "parent"

    log_entry = {
        "timestamp_utc": timestamp_utc,
        "event_type": event_type,
        "task_role": task_role,
        "task_id": task.task_id,
        "parent_task_id": task.parent_task_id,
        "agent": task.agent.name,
        "intent": task.intent.action,
        "risk_level": task.risk_level,
        "human_review_required": task.human_review_required,
        "decision": decision,
        "reason": reason,
        "status": task.result.status
    }

    with open("audit_log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
