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