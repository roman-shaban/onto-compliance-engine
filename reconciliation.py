import json
import os
from typing import Dict, List, Optional

from onto_models import OntoTask
from persistence import save_task
from recovery import load_task_by_id


STORAGE_DIR = "storage"
TASKS_FILE = os.path.join(STORAGE_DIR, "tasks.json")


def _load_tasks() -> Dict[str, dict]:
    if not os.path.exists(TASKS_FILE):
        raise FileNotFoundError("tasks.json not found. Run the system first.")
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_children_of_parent(parent_task_id: str) -> List[dict]:
    tasks = _load_tasks()
    children = [
        task for task in tasks.values()
        if task.get("parent_task_id") == parent_task_id
    ]
    children.sort(key=lambda t: t.get("timestamp", ""))
    return children


def reconcile_parent(parent_task_id: str) -> Optional[OntoTask]:
    parent_task = load_task_by_id(parent_task_id)
    if parent_task is None:
        print(f"Parent task not found: {parent_task_id}")
        return None

    children = get_children_of_parent(parent_task_id)

    print("=== RECONCILIATION REQUEST ===")
    print(f"Parent task ID: {parent_task.task_id}")
    print(f"Parent current status: {parent_task.result.status}")
    print(f"Found children: {len(children)}")

    if not children:
        print("No child tasks found. Nothing to reconcile.")
        return parent_task

    child_statuses = [child.get("status") for child in children]
    print("Child statuses:", child_statuses)

    # Rule 1: if any child is blocked -> parent stays failed
    if any(status == "blocked" for status in child_statuses):
        parent_task.result.status = "failed"
        parent_task.result.output = "Reconciliation: parent remains failed because at least one child is blocked"
        save_task(parent_task)

        print("Reconciliation result: parent remains failed (blocked child exists)")
        return parent_task

    # Rule 2: if any child is failed -> parent stays failed
    if any(status == "failed" for status in child_statuses):
        parent_task.result.status = "failed"
        parent_task.result.output = "Reconciliation: parent remains failed because at least one child failed"
        save_task(parent_task)

        print("Reconciliation result: parent remains failed (failed child exists)")
        return parent_task

    # Rule 3: if all children completed -> parent becomes completed
    if all(status == "completed" for status in child_statuses):
        parent_task.result.status = "completed"
        parent_task.result.output = "Reconciled: all child tasks completed successfully"
        save_task(parent_task)

        print("Reconciliation result: parent updated to completed")
        return parent_task

    # Rule 4: otherwise leave unchanged
    print("Reconciliation result: no change")
    return parent_task


def reconcile_from_child(child_task_id: str) -> Optional[OntoTask]:
    child_task = load_task_by_id(child_task_id)
    if child_task is None:
        print(f"Child task not found: {child_task_id}")
        return None

    parent_task_id = child_task.parent_task_id
    if not parent_task_id:
        print("This task has no parent. Nothing to reconcile.")
        return child_task

    return reconcile_parent(parent_task_id)