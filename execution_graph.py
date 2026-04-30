# Copyright (c) 2026 Roman Shaban. All rights reserved.
# Licensed under the Apache License 2.0.
# Part of the CIOS / Onto-Protocol Ecosystem.
from typing import Dict, List, Optional
from onto_models import OntoTask
import uuid


class ExecutionGraph:
    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id or str(uuid.uuid4())
        self.nodes: Dict[str, OntoTask] = {}
        self.children: Dict[str, List[str]] = {}

    def add_task(self, task: OntoTask):
        task.run_id = self.run_id
        self.nodes[task.task_id] = task

        if task.parent_task_id:
            if task.parent_task_id not in self.children:
                self.children[task.parent_task_id] = []
            if task.task_id not in self.children[task.parent_task_id]:
                self.children[task.parent_task_id].append(task.task_id)

    def display(self):
        print(f"\n=== EXECUTION GRAPH (run_id={self.run_id}) ===")

        roots = [
            tid for tid, task in self.nodes.items()
            if task.parent_task_id is None
        ]

        for root_id in roots:
            self._print_tree(root_id, 0)

    def _print_tree(self, task_id: str, level: int):
        task = self.nodes[task_id]
        indent = "  " * level
        print(f"{indent}- {task.agent.name} | {task.intent.action} | {task.result.status}")

        for child_id in self.children.get(task_id, []):
            self._print_tree(child_id, level + 1)
