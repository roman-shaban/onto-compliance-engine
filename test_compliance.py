from recovery import load_task_by_id
from compliance_engine import (
    evaluate_task_compliance,
    save_compliance_record,
    summarize_run_compliance,
)

# Use a real existing task_id from your storage/tasks.json
TASK_ID = "1f58b065-76f4-4fff-bd86-f7dba7b4b1c9"


task = load_task_by_id(TASK_ID)

if task is None:
    print("Task not found.")
else:
    record = evaluate_task_compliance(task)
    save_compliance_record(record)

    print("=== TASK COMPLIANCE SUMMARY ===")
    print("Task ID:", record.task_id)
    print("Run ID:", record.run_id)
    print("Agent:", record.agent_name)
    print("Intent:", record.intent_action)
    print("Task Status:", record.task_status)
    print("Compliance Status:", record.compliance_status)
    print("Risk Score:", record.risk_score)
    print("Trust Score:", record.trust_score)
    print("Proof Score:", record.proof_score)
    print("Review Status:", record.review_status)
    print("Incident Flags:", record.incident_flags)
    print("Final Verdict:", record.final_verdict)
    print("Notes:", record.notes)

    print("\n=== PROOF RECORD ===")
    print("Proof Status:", record.proof.proof_status)
    print("Execution Trace Present:", record.proof.execution_trace_present)
    print("Policy Trace Present:", record.proof.policy_trace_present)
    print("Approval Trace Present:", record.proof.approval_trace_present)
    print("Replayable:", record.proof.replayable)
    print("Confidence Level:", record.proof.confidence_level)

    print("\n=== RUN COMPLIANCE SUMMARY ===")
    run_summary = summarize_run_compliance(task.run_id)
    for key, value in run_summary.items():
        print(f"{key}: {value}")