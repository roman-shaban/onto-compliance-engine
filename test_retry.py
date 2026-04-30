# Copyright (c) 2026 Roman Shaban. All rights reserved.
# Licensed under the Apache License 2.0.
# Part of the CIOS / Onto-Protocol Ecosystem.
import json
import os
from recovery import retry_task

TASKS_FILE = os.path.join("storage", "tasks.json")


def find_latest_blocked_task_id():
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    blocked_tasks = [
        task for task in tasks.values()
        if task.get("status") == "blocked"
    ]

    if not blocked_tasks:
        return None

    blocked_tasks.sort(key=lambda t: t.get("timestamp", ""), reverse=True)
    return blocked_tasks[0]["task_id"]


task_id = find_latest_blocked_task_id()

if task_id is None:
    print("No blocked task found in storage/tasks.json")
else:
    print(f"Latest blocked task found: {task_id}")
    retry_task(task_id, auto_approve=True, keep_approval=True)
