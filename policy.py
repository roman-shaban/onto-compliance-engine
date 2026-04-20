from onto_models import OntoTask


def evaluate_policies(task: OntoTask):
    """
    Returns structured policy evaluation result:
    {
        "decision": "allowed" | "blocked",
        "violations": [...],
        "summary": str
    }
    """

    violations = []

    # RULE 1: High risk must be blocked
    if task.risk_level == "high":
        violations.append("high_risk")

    # RULE 2: Human review required, unless already approved
    if task.human_review_required and not task.human_approved:
        violations.append("human_review_required")

    # RULE 3: Forbidden action
    if task.intent.action in task.permissions.forbidden:
        violations.append("forbidden_action")

    if violations:
        return {
            "decision": "blocked",
            "violations": violations,
            "summary": ", ".join(violations)
        }

    return {
        "decision": "allowed",
        "violations": [],
        "summary": "conditions_met"
    }