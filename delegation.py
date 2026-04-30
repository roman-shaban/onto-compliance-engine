# Copyright (c) 2026 Roman Shaban. All rights reserved.
# Licensed under the Apache License 2.0.
# Part of the CIOS / Onto-Protocol Ecosystem.
from onto_models import OntoTask


def delegate_task(parent_task: OntoTask, new_agent: str, new_intent: str):
    print("\nDELEGATION INITIATED")

    subtask = OntoTask(
        agent={"name": new_agent},
        intent={"action": new_intent},
        input=parent_task.input,
        expected_output=parent_task.expected_output,
        permissions=parent_task.permissions,
        risk_level=parent_task.risk_level,
        human_review_required=parent_task.human_review_required,
        human_approved=parent_task.human_approved,
        parent_task_id=parent_task.task_id,
        depth=parent_task.depth + 1,
        result={"status": "pending", "output": None}
    )

    print(f"Delegated from {parent_task.agent.name} -> {new_agent}")
    print(f"New intent: {new_intent}")
    print(f"New depth: {subtask.depth}")
    print(f"Inherited human_approved: {subtask.human_approved}")

    return subtask
