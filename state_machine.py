from onto_models import OntoTask


ALLOWED_TRANSITIONS = {
    "pending": ["running", "blocked", "failed"],
    "running": ["completed", "blocked", "failed"],
    "blocked": [],
    "failed": [],
    "completed": []
}


def transition_task(task: OntoTask, new_status: str, output: str | None = None):
    current_status = task.result.status

    if new_status not in ALLOWED_TRANSITIONS[current_status]:
        raise ValueError(
            f"Invalid state transition: {current_status} -> {new_status}"
        )

    task.result.status = new_status

    if output is not None:
        task.result.output = output

    return task