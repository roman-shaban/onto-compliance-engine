from delegation import delegate_task
from onto_models import OntoTask
from audit import log_event
from policy import evaluate_policies
from state_machine import transition_task
from execution_graph import ExecutionGraph
from persistence import save_task, save_run
from compliance_engine import (
    evaluate_task_compliance,
    save_compliance_record,
    summarize_run_compliance,
)
from incident_engine import build_incident_report


MAX_DELEGATION_DEPTH = 2


def print_incident_report(record):
    if not record.incident_flags:
        return

    task_ctx = {
        "task_id": record.task_id,
        "run_id": record.run_id,
        "agent_name": record.agent_name,
        "intent_action": record.intent_action,
        "task_status": record.task_status,
        "compliance_status": record.compliance_status,
        "risk_score": record.risk_score,
        "trust_score": record.trust_score,
        "proof_score": record.proof_score,
        "review_status": record.review_status,
        "final_verdict": record.final_verdict,
    }

    incidents = build_incident_report(record.incident_flags, task_ctx)

    print("\n=== INCIDENT REPORT ===")
    for incident in incidents:
        print(f"Type: {incident['type']}")
        print(f"Severity: {incident['severity']}")
        print(f"Reason: {incident['reason']}")
        print(f"Action: {incident['action']}")
        print("---")


def print_compliance_summary(task: OntoTask):
    record = evaluate_task_compliance(task)
    save_compliance_record(record)

    print("\n=== TASK COMPLIANCE SUMMARY ===")
    print(f"Task ID: {record.task_id}")
    print(f"Run ID: {record.run_id}")
    print(f"Agent: {record.agent_name}")
    print(f"Intent: {record.intent_action}")
    print(f"Task Status: {record.task_status}")
    print(f"Compliance Status: {record.compliance_status}")
    print(f"Risk Score: {record.risk_score}")
    print(f"Trust Score: {record.trust_score}")
    print(f"Proof Score: {record.proof_score}")
    print(f"Review Status: {record.review_status}")
    print(f"Incident Flags: {record.incident_flags}")
    print(f"Final Verdict: {record.final_verdict}")
    print(f"Notes: {record.notes}")

    if getattr(record, "proof", None) is not None:
        print("\n=== PROOF RECORD ===")
        print(f"Proof Status: {record.proof.proof_status}")
        print(f"Execution Trace Present: {record.proof.execution_trace_present}")
        print(f"Policy Trace Present: {record.proof.policy_trace_present}")
        print(f"Approval Trace Present: {record.proof.approval_trace_present}")
        print(f"Replayable: {record.proof.replayable}")
        print(f"Confidence Level: {record.proof.confidence_level}")

    print_incident_report(record)

    return record


def print_run_compliance_summary(run_id: str):
    summary = summarize_run_compliance(run_id)

    print("\n=== RUN COMPLIANCE SUMMARY ===")
    print(f"run_id: {summary['run_id']}")
    print(f"task_count: {summary['task_count']}")
    print(f"blocked_count: {summary['blocked_count']}")
    print(f"failed_count: {summary['failed_count']}")
    print(f"completed_count: {summary['completed_count']}")
    print(f"high_risk_task_count: {summary['high_risk_task_count']}")
    print(f"incidents: {summary['incidents']}")
    print(f"overall_verdict: {summary['overall_verdict']}")

    return summary


def run_task(task: OntoTask, graph: ExecutionGraph = None):
    root_call = graph is None

    if graph is None:
        graph = ExecutionGraph(run_id=task.run_id)

        if task.run_id is None:
            task.run_id = graph.run_id

        save_run(task.run_id)

    elif task.run_id is None:
        task.run_id = graph.run_id

    graph.add_task(task)

    print("=== RUNNING TASK ===")

    if task.result.status == "pending":
        transition_task(task, "running")
    elif task.result.status == "running":
        pass
    else:
        raise ValueError(
            f"run_task cannot start task from status: {task.result.status}"
        )

    save_task(task)

    print(f"Agent: {task.agent.name}")
    print(f"Intent: {task.intent.action}")
    print(f"Task ID: {task.task_id}")
    print(f"Run ID: {task.run_id}")
    print(f"Parent Task ID: {task.parent_task_id}")
    print(f"Depth: {task.depth}")

    print("Input:", task.input)
    print("Expected output:", task.expected_output)

    print("Permissions:")
    print("  Allowed:", task.permissions.allowed)
    print("  Forbidden:", task.permissions.forbidden)

    print("Risk level:", task.risk_level)
    print("Human review required:", task.human_review_required)
    print("Human approved:", task.human_approved)

    log_event(
        task,
        event_type="task_started",
        decision="started",
        reason="run_task_called"
    )

    subtask = None
    can_delegate = task.depth < MAX_DELEGATION_DEPTH

    if task.intent.action == "create_business_plan" and can_delegate:
        print("\nDelegating market analysis...")

        log_event(
            task,
            event_type="delegation_created",
            decision="delegated",
            reason="market_analysis_subtask_created"
        )

        subtask = delegate_task(
            task,
            new_agent="Market Analyst",
            new_intent="analyze_market"
        )

        subtask.run_id = task.run_id

        print("\n--- RUNNING SUBTASK ---")
        run_task(subtask, graph)

        print("\n--- SUBTASK RESULT RETURNED ---")
        print(f"Subtask status: {subtask.result.status}")
        print(f"Subtask output: {subtask.result.output}")

        log_event(
            task,
            event_type="subtask_result_received",
            decision="received",
            reason=f"subtask_status={subtask.result.status}"
        )

        if subtask.result.status == "blocked":
            transition_task(
                task,
                "failed",
                f"Parent failed because subtask was blocked: {subtask.result.output}"
            )
            save_task(task)

            log_event(
                task,
                event_type="task_failed",
                decision="failed",
                reason="subtask_blocked"
            )

            print("\nPARENT TASK FAILED DUE TO SUBTASK BLOCK")
            print("Status:", task.result.status)
            print("Output:", task.result.output)

            print_compliance_summary(task)

            print("\n=== EXECUTION GRAPH ===")
            graph.display()

            if root_call:
                print_run_compliance_summary(task.run_id)

            return task

        if subtask.result.status == "failed":
            transition_task(
                task,
                "failed",
                f"Parent failed because subtask failed: {subtask.result.output}"
            )
            save_task(task)

            log_event(
                task,
                event_type="task_failed",
                decision="failed",
                reason="subtask_failed"
            )

            print("\nPARENT TASK FAILED DUE TO SUBTASK FAILURE")
            print("Status:", task.result.status)
            print("Output:", task.result.output)

            print_compliance_summary(task)

            print("\n=== EXECUTION GRAPH ===")
            graph.display()

            if root_call:
                print_run_compliance_summary(task.run_id)

            return task

    elif task.intent.action == "create_business_plan" and not can_delegate:
        print("\nDelegation blocked: max depth reached")

        log_event(
            task,
            event_type="delegation_blocked",
            decision="blocked",
            reason="max_delegation_depth_reached"
        )

    policy_result = evaluate_policies(task)

    print(f"\nPolicy decision: {policy_result['decision']}")
    print(f"Policy summary: {policy_result['summary']}")

    if policy_result["violations"]:
        print("Violations:")
        for violation in policy_result["violations"]:
            print(f" - {violation}")

    if policy_result["decision"] == "blocked":
        transition_task(
            task,
            "blocked",
            f"Blocked by policy: {policy_result['summary']}"
        )
        save_task(task)

        log_event(
            task,
            event_type="task_blocked",
            decision=policy_result["decision"],
            reason=policy_result["summary"]
        )

        print_compliance_summary(task)

        print("\n=== EXECUTION GRAPH ===")
        graph.display()

        if root_call:
            print_run_compliance_summary(task.run_id)

        return task

    print("\nTask allowed to proceed")

    if subtask is not None:
        output = f"Parent task completed after subtask with status: {subtask.result.status}"
    else:
        output = "Simulated execution result"

    transition_task(task, "completed", output)
    save_task(task)

    log_event(
        task,
        event_type="task_completed",
        decision=policy_result["decision"],
        reason=policy_result["summary"]
    )

    print("Status:", task.result.status)
    print("Output:", task.result.output)
    print("=== TASK FINISHED ===")

    print_compliance_summary(task)

    print("\n=== EXECUTION GRAPH ===")
    graph.display()

    if root_call:
        print_run_compliance_summary(task.run_id)

    return task


if __name__ == "__main__":
    root_task = OntoTask(
        agent={"name": "Business Analyst"},
        intent={"action": "create_business_plan"},
        input={"business": "AI Compliance Startup"},
        expected_output={"type": "business_plan"},
        permissions={
            "allowed": ["analyze_market", "write_plan"],
            "forbidden": ["access_bank_account"]
        },
        risk_level="low",
        human_review_required=True,
        result={"status": "pending", "output": None},
    )

    run_task(root_task)