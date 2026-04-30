# Copyright (c) 2026 Roman Shaban. All rights reserved.
# Licensed under the Apache License 2.0.
# Part of the CIOS / Onto-Protocol Ecosystem.
from typing import List, Dict


def classify_incident(flag: str, task_ctx: Dict) -> Dict:
    if flag == "policy_block":
        return {
            "type": "policy_block",
            "severity": "high",
            "reason": "Blocked by policy",
            "action": "review policy rules"
        }

    if flag == "failed_execution":
        return {
            "type": "failed_execution",
            "severity": "high",
            "reason": "Task execution failed",
            "action": "retry or debug execution"
        }

    if flag == "human_review_missing":
        return {
            "type": "human_review_missing",
            "severity": "medium",
            "reason": "Human approval required but not provided",
            "action": "request human approval"
        }

    if flag == "low_proof_score":
        return {
            "type": "low_proof_score",
            "severity": "medium",
            "reason": "Insufficient audit/proof data",
            "action": "improve logging or replayability"
        }

    return {
        "type": flag,
        "severity": "low",
        "reason": "Unknown issue",
        "action": "inspect manually"
    }


def build_incident_report(flags: List[str], task_ctx: Dict) -> List[Dict]:
    return [classify_incident(flag, task_ctx) for flag in flags]
