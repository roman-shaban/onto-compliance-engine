import json
import os
from typing import Optional
from onto_models import OntoTask
from approval import approve_task
from runner import run_task


STORAGE_DIR = "storage"
TASKS_FILE = os.path.join(STORAGE_DIR, "tasks.json")


def _load_tasks():
    if not os.path.exists(TASKS_FILE):
        raise FileNotFoundError("tasks.json not found. Run the system first.")
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_task_by_id(task_id: str) -> Optional[OntoTask]:
    tasks = _load_tasks()

    data = tasks.get(task_id)
    if not data:
        return None

    task = OntoTask(
        task_id=data["task_id"],
        parent_task_id=data.get("parent_task_id"),
        depth=data.get("depth", 0),
        run_id=data.get("run_id"),
        agent={"name": data["agent"]},
        intent={"action": data["intent"]},
        input=data.get("input", {}),
        expected_output=data.get("expected_output", {}),
        permissions={
            "allowed": ["analyze", "forecast"],
            "forbidden": ["spend_money"]
        },
        risk_level=data.get("risk_level", "low"),
        human_review_required=data.get("human_review_required", True),
        human_approved=data.get("human_approved", False),
        result={
            "status": data.get("status", "pending"),
            "output": data.get("output")
        }
    )

    return task


def show_task_summary(task_id: str):
    task = load_task_by_id(task_id)

    if task is None:
        print(f"Task not found: {task_id}")
        return

    print("=== TASK RECOVERY SUMMARY ===")
    print(f"Task ID: {task.task_id}")
    print(f"Run ID: {task.run_id}")
    print(f"Parent Task ID: {task.parent_task_id}")
    print(f"Agent: {task.agent.name}")
    print(f"Intent: {task.intent.action}")
    print(f"Depth: {task.depth}")
    print(f"Status: {task.result.status}")
    print(f"Output: {task.result.output}")
    print(f"Human review required: {task.human_review_required}")
    print(f"Human approved: {task.human_approved}")


def resume_task(task_id: str, auto_approve: bool = False):
    task = load_task_by_id(task_id)

    if task is None:
        print(f"Task not found: {task_id}")
        return None

    print("=== RESUME REQUEST ===")
    print(f"Task ID: {task.task_id}")
    print(f"Current status: {task.result.status}")
    print(f"Human approved: {task.human_approved}")

    if task.result.status == "completed":
        print("Task is already completed. Nothing to resume.")
        return task

    if task.result.status in ["blocked", "failed"]:
        if auto_approve:
            print("Auto-approving recovered task...")
            approve_task(task)
        else:
            print("Task is blocked/failed. Resume requires approval.")
            return task

    if task.result.status == "running":
        print("Recovered task was left in running state. Resetting to pending for safe resume.")
        task.result.status = "pending"
        task.result.output = "Recovered from interrupted running state"

    if task.result.status != "pending":
        print(f"Task not resumable from status: {task.result.status}")
        return task

    print("\n=== RESUMING TASK ===")
    return run_task(task)


def retry_task(task_id: str, auto_approve: bool = False, keep_approval: bool = True):
    task = load_task_by_id(task_id)

    if task is None:
        print(f"Task not found: {task_id}")
        return None

    print("=== RETRY REQUEST ===")
    print(f"Task ID: {task.task_id}")
    print(f"Current status: {task.result.status}")
    print(f"Current output: {task.result.output}")
    print(f"Human approved before retry: {task.human_approved}")

    if task.result.status == "completed":
        print("Task is already completed. Retry not needed.")
        return task

    if task.result.status not in ["blocked", "failed"]:
        print(f"Retry not supported from status: {task.result.status}")
        return task

    if auto_approve:
        print("Auto-approving task before retry...")
        approve_task(task)
    else:
        task.result.status = "pending"
        task.result.output = "Retry requested manually"

        if not keep_approval:
            task.human_approved = False

    print("\n=== RETRYING TASK ===")
    print(f"Status before rerun: {task.result.status}")
    print(f"Human approved before rerun: {task.human_approved}")

    return run_task(task)