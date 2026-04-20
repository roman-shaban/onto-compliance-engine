from recovery import resume_task

# blocked task from your storage/tasks.json
TASK_ID = "92b71709-28c4-4085-af09-8adada95cf40"

resume_task(TASK_ID, auto_approve=True)