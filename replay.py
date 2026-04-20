import json
import os
from typing import List, Dict, Optional


STORAGE_DIR = "storage"
TASKS_FILE = os.path.join(STORAGE_DIR, "tasks.json")
RUNS_FILE = os.path.join(STORAGE_DIR, "runs.json")


def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_tasks() -> Dict[str, dict]:
    return _load_json(TASKS_FILE)


def load_all_runs() -> Dict[str, dict]:
    return _load_json(RUNS_FILE)


def get_tasks_by_run_id(run_id: str) -> List[dict]:
    tasks = load_all_tasks()

    run_tasks = [
        task for task in tasks.values()
        if task.get("run_id") == run_id
    ]

    run_tasks.sort(
        key=lambda t: (
            t.get("depth", 0),
            t.get("timestamp", ""),
            t.get("task_id", "")
        )
    )

    return run_tasks


def get_latest_run_id() -> Optional[str]:
    runs = load_all_runs()

    if not runs:
        return None

    run_items = list(runs.values())
    run_items.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
    return run_items[0]["run_id"]


def show_run_summary(run_id: str):
    run_tasks = get_tasks_by_run_id(run_id)

    print("=== RUN SUMMARY ===")
    print(f"Run ID: {run_id}")
    print(f"Task count: {len(run_tasks)}")

    if not run_tasks:
        print("No tasks found for this run.")
        return

    status_counts = {}
    for task in run_tasks:
        status = task.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    print("Status breakdown:")
    for status, count in status_counts.items():
        print(f" - {status}: {count}")


def replay_run(run_id: str):
    run_tasks = get_tasks_by_run_id(run_id)

    print("=== REPLAY ENGINE ===")
    print(f"Run ID: {run_id}")
    print(f"Found tasks: {len(run_tasks)}")

    if not run_tasks:
        print("No tasks found for this run.")
        return

    print("\n=== REPLAY STEPS ===")

    for index, task in enumerate(run_tasks, start=1):
        print(f"\nStep {index}")
        print(f"Task ID: {task.get('task_id')}")
        print(f"Parent Task ID: {task.get('parent_task_id')}")
        print(f"Agent: {task.get('agent')}")
        print(f"Intent: {task.get('intent')}")
        print(f"Depth: {task.get('depth')}")
        print(f"Status: {task.get('status')}")
        print(f"Output: {task.get('output')}")
        print(f"Human approved: {task.get('human_approved')}")
        print(f"Timestamp: {task.get('timestamp')}")


def replay_latest_run():
    run_id = get_latest_run_id()

    if run_id is None:
        print("No runs found.")
        return

    show_run_summary(run_id)
    print()
    replay_run(run_id)