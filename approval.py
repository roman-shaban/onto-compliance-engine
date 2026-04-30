# Copyright (c) 2026 Roman Shaban. All rights reserved.
# Licensed under the Apache License 2.0.
# Part of the CIOS / Onto-Protocol Ecosystem.
from onto_models import OntoTask


def approve_task(task: OntoTask):
    if task.result.status not in ["blocked", "failed"]:
        raise ValueError(f"Cannot approve task with status: {task.result.status}")

    task.human_approved = True
    task.result.status = "pending"
    task.result.output = "Approved by human reviewer"

    return task


def reject_task(task: OntoTask):
    if task.result.status not in ["blocked", "failed"]:
        raise ValueError(f"Cannot reject task with status: {task.result.status}")

    task.human_approved = False
    task.result.status = "failed"
    task.result.output = "Rejected by human reviewer"

    return task
