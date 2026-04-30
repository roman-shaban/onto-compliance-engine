# Copyright (c) 2026 Roman Shaban. All rights reserved.
# Licensed under the Apache License 2.0.
# Part of the CIOS / Onto-Protocol Ecosystem.
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import uuid


class Agent(BaseModel):
    name: str


class Intent(BaseModel):
    action: str


class Permissions(BaseModel):
    allowed: List[str]
    forbidden: List[str]


class Result(BaseModel):
    status: str = "pending"
    output: Optional[str] = None


class OntoTask(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    parent_task_id: Optional[str] = None
    depth: int = 0

    # 🔥 НОВЕ
    run_id: Optional[str] = None

    agent: Agent
    intent: Intent

    input: Dict
    expected_output: Dict

    permissions: Permissions

    risk_level: str = "low"
    human_review_required: bool = True

    # approval system
    human_approved: bool = False

    result: Result = Field(default_factory=Result)
