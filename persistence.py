import json
import os
from datetime import datetime
from typing import Optional
from onto_models import OntoTask


STORAGE_DIR = "storage"
TASKS_FILE = os.path.join(STORAGE_DIR, "tasks.json")
RUNS_FILE = os.path.join(STORAGE_DIR, "runs.json")


def _ensure_storage():
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "w") as f:
            json.dump({}, f)

    if not os.path.exists(RUNS_FILE):
        with open(RUNS_FILE, "w") as f:
            json.dump({}, f)


def _load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def _save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def save_task(task: OntoTask):
    _ensure_storage()

    tasks = _load_json(TASKS_FILE)

    tasks[task.task_id] = {
        "task_id": task.task_id,
        "parent_task_id": task.parent_task_id,
        "agent": task.agent.name,
        "intent": task.intent.action,
        "input": task.input,
        "expected_output": task.expected_output,
        "status": task.result.status,
        "output": task.result.output,
        "depth": task.depth,
        "run_id": task.run_id,
        "human_approved": getattr(task, "human_approved", False),
        "timestamp": datetime.utcnow().isoformat()
    }

    _save_json(TASKS_FILE, tasks)


def save_run(run_id: str):
    _ensure_storage()

    runs = _load_json(RUNS_FILE)

    runs[run_id] = {
        "run_id": run_id,
        "timestamp": datetime.utcnow().isoformat()
    }

    _save_json(RUNS_FILE, runs)


def get_task(task_id: str) -> Optional[dict]:
    _ensure_storage()

    tasks = _load_json(TASKS_FILE)
    return tasks.get(task_id)


def get_all_tasks():
    _ensure_storage()
    return _load_json(TASKS_FILE)


def get_all_runs():
    _ensure_storage()
    return _load_json(RUNS_FILE)