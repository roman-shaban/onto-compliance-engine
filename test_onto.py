# Copyright (c) 2026 Roman Shaban. All rights reserved.
# Licensed under the Apache License 2.0.
# Part of the CIOS / Onto-Protocol Ecosystem.
from onto_models import OntoTask
from runner import run_task


task = OntoTask(
    agent={"name": "Business Analyst"},
    intent={"action": "create_business_plan"},
    input={"niche": "AI services", "budget": 1000},
    expected_output={"deliverables": ["3 strategies", "forecast"]},
    permissions={
        "allowed": ["analyze", "forecast"],
        "forbidden": ["spend_money"]
    },
    risk_level="low",
    human_review_required=True,
    human_approved=False,  # deliberately false to create a blocked child
    result={"status": "pending", "output": None}
)

run_task(task)
