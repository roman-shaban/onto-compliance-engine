# ONTO SPEC v1

## 1. Purpose

The Onto Protocol defines a standardized structure for representing, validating, and executing AI-driven tasks.

It provides a formal model for how intelligent agents:

- express intent
- operate within defined permissions
- manage risk and human oversight
- produce structured and verifiable outcomes

The protocol is designed to ensure:

- consistency across AI systems
- interpretability of actions
- enforceable constraints (permissions, risk levels)
- traceability of execution

Onto serves as a foundational layer for building reliable, auditable, and interoperable AI systems.

## 2. Scope

The Onto Protocol specifies:

- the structure of task definitions
- the representation of agents and their capabilities
- the formal model of intent and execution context
- permission constraints and policy boundaries
- risk classification and human-in-the-loop requirements
- the structure and semantics of outcomes
- error categorization and handling

The protocol does NOT define:

- internal implementation of AI models
- specific algorithms for decision-making
- user interfaces or external system integrations

Onto focuses strictly on the standardization of interaction, validation, and execution semantics between components.

## 3. Core Concepts

The Onto Protocol is built around the following core concepts:

### Agent
An entity capable of executing tasks. An agent has an identity and operates within defined permissions.

### Intent
A formal representation of a desired action or goal. Intent defines what needs to be done, not how it is implemented.

### Task
A structured unit of work that combines an agent, intent, input data, constraints, and expected outcomes.

### Permissions
A set of constraints that define what actions are allowed or forbidden during task execution.

### Risk Level
A classification of the potential impact or sensitivity of a task. Determines whether human review is required.

### Human Review
A control mechanism that enforces human approval before execution under certain risk conditions.

### Result
A structured representation of the outcome of a task, including status and output data.

### Execution Context
The full set of conditions under which a task is evaluated and executed, including permissions, risk, and input.

## 4. Object Model

The Onto Protocol defines a structured object model for representing tasks.

A task is composed of the following elements:

### 4.1 Agent
Represents the entity performing the task.

Attributes:
- name: identifier of the agent

---

### 4.2 Intent
Defines the action or goal of the task.

Attributes:
- action: the type of operation to be performed

---

### 4.3 Input
Represents the data required to execute the task.

Attributes:
- arbitrary key-value structure

---

### 4.4 Expected Output
Defines the expected deliverables of the task.

Attributes:
- deliverables: list of expected outputs

---

### 4.5 Permissions
Defines constraints on allowed and forbidden actions.

Attributes:
- allowed: list of permitted actions
- forbidden: list of prohibited actions

---

### 4.6 Risk Level
Classifies the sensitivity or potential impact of the task.

Allowed values:
- low
- medium
- high

---

### 4.7 Human Review Required
Indicates whether human approval is required before execution.

Allowed values:
- true
- false

---

### 4.8 Result
Represents the outcome of the task.

Attributes:
- status: current state of execution
- output: resulting data (optional)

Allowed status values:
- pending
- completed
- failed
- blocked

## 5. Intent Model

The Intent Model defines the formal representation of actions within the Onto Protocol.

Intent is the central component of a task. It specifies what is to be done, independent of implementation.

### 5.1 Intent Structure

An intent is defined by:

- action: a symbolic representation of the operation to be performed
- goal (optional): a higher-level description of the objective

---

### 5.2 Intent Semantics

Intent must be:

- explicit: clearly defined and unambiguous
- atomic: represent a single logical action
- context-independent: not tied to a specific implementation

---

### 5.3 Allowed Intent Types

Intent types may include (but are not limited to):

- analyze
- plan
- generate
- evaluate
- transform
- validate

---

### 5.4 Intent Constraints

Intent must not:

- imply execution beyond defined permissions
- encode hidden instructions
- depend on unspecified external context

---

### 5.5 Intent and Execution

Intent defines the expected operation, but execution is governed by:

- permissions
- risk level
- human review requirements

Intent alone does not authorize execution.

## 6. Delegation Model

The Delegation Model defines how authority is transferred or assigned between entities within the Onto Protocol.

Delegation determines who is allowed to act, under what conditions, and within which boundaries.

### 6.1 Delegation Principles

- all actions must be attributable to an agent
- delegation must be explicit, not implicit
- authority is limited by permissions and context

---

### 6.2 Acting Modes

An agent may operate in one of the following modes:

- self: acting on its own authority
- on_behalf_of_user: acting as a proxy for a human
- on_behalf_of_agent: acting under delegation from another agent

---

### 6.3 Delegation Constraints

Delegation must enforce:

- permission boundaries
- risk restrictions
- human review requirements

An agent must not:

- exceed delegated authority
- bypass forbidden actions
- act without traceability

---

### 6.4 Delegation Traceability

All delegated actions must be traceable to:

- the originating agent or user
- the chain of delegation

This ensures accountability and auditability.

---

### 6.5 Delegation and Execution

Delegation does not guarantee execution.

Execution is allowed only if:

- permissions are satisfied
- risk conditions are met
- required approvals are obtained

## 7. Trust Model

The Trust Model defines how reliability, authenticity, and integrity are established within the Onto Protocol.

Trust ensures that actions, data, and outcomes can be verified and relied upon.

### 7.1 Trust Principles

- all actions must be attributable
- all data must be verifiable
- trust must be explicitly defined, not assumed

---

### 7.2 Identity

Each agent must have a defined identity.

Identity ensures:

- uniqueness of the agent
- traceability of actions
- accountability

---

### 7.3 Verification

All critical elements must be verifiable:

- task definitions
- execution results
- delegation chains

Verification may include:

- structural validation (schema)
- logical validation (constraints)
- external validation (human or system)

---

### 7.4 Provenance

Provenance refers to the origin and history of data and actions.

The system must be able to track:

- where data comes from
- which agent produced it
- how it was transformed

---

### 7.5 Trust Levels

Trust may be classified into levels:

- low: unverified data or actions
- medium: internally validated
- high: externally verified or audited

---

### 7.6 Trust and Execution

Execution must consider trust level:

- low trust may restrict execution
- high-risk actions require higher trust
- insufficient trust may trigger human review

## 8. Outcome Model

The Outcome Model defines how the result of a task is represented, interpreted, and evaluated.

Outcome provides a structured view of what happened during execution.

### 8.1 Outcome Structure

An outcome includes:

- status: the state of the task
- output: the resulting data (optional)

---

### 8.2 Status Values

The status field must be one of the following:

- pending: task has not yet been executed
- completed: task was successfully executed
- failed: execution encountered an error
- blocked: execution was stopped due to constraints (e.g. permissions, risk)

---

### 8.3 Outcome Semantics

Outcome must be:

- explicit: clearly indicate the state of execution
- consistent: follow defined status values
- interpretable: understandable across systems

---

### 8.4 Outcome and Validation

Outcome must reflect:

- whether execution was allowed
- whether constraints were satisfied
- whether the result is usable

---

### 8.5 Outcome and Trust

Outcome reliability depends on:

- trust level of the agent
- verification of execution
- traceability of actions

Low trust outcomes may require further validation or rejection.

## 9. Error Model

The Error Model defines how failures, violations, and inconsistencies are represented and handled within the Onto Protocol.

Errors are treated as structured and meaningful events, not just system failures.

---

### 9.1 Error Categories

Errors are classified into the following categories:

#### Validation Errors
- Occur when input data does not conform to the defined schema
- Example: invalid data types, missing required fields

#### Execution Errors
- Occur during task execution
- Example: runtime failures, unexpected conditions

#### Permission Violations
- Occur when an action exceeds allowed permissions
- Example: attempting forbidden operations

#### Risk Violations
- Occur when risk constraints are not satisfied
- Example: high-risk task without required human review

#### Trust Violations
- Occur when trust conditions are not met
- Example: unverified agent, missing provenance

---

### 9.2 Error Structure

An error should include:

- type: category of the error
- message: human-readable description
- context: relevant data or conditions

---

### 9.3 Error Handling Principles

- errors must be explicit and structured
- errors must not be silently ignored
- errors must preserve system integrity

---

### 9.4 Error and Execution

When an error occurs:

- execution must be stopped or adjusted
- the outcome must reflect the failure
- relevant error information must be recorded

---

### 9.5 Error and Compliance

Errors are critical for:

- auditing system behavior
- enforcing constraints
- maintaining trust and accountability

Unresolved errors may trigger:

- human review
- rejection of results
- system-level alerts

## 10. Message Structure

The Onto Protocol defines a standard message structure for representing tasks in a machine-readable format.

The canonical format of an Onto message is JSON.

---

### 10.1 Onto Message Schema

An Onto message must include:

- agent
- intent
- input
- expected_output
- permissions
- risk_level
- human_review_required
- result

---

### 10.2 Example Onto Message

```json
{
  "agent": {
    "name": "Business Analyst"
  },
  "intent": {
    "action": "create_business_plan"
  },
  "input": {
    "niche": "AI services",
    "budget": 1000
  },
  "expected_output": {
    "deliverables": ["3 strategies", "forecast"]
  },
  "permissions": {
    "allowed": ["analyze", "forecast"],
    "forbidden": ["spend_money"]
  },
  "risk_level": "low",
  "human_review_required": true,
  "result": {
    "status": "pending",
    "output": null
  }
}
```

## 11. Conformance

The Conformance section defines the requirements for a system to be considered compliant with the Onto Protocol.

---

### 11.1 Conformance Requirements

A system is considered Onto-compliant if it:

- correctly implements the Onto object model
- validates tasks according to the defined schema
- enforces permissions and risk constraints
- produces outcomes following the defined outcome model
- handles errors according to the error model

---

### 11.2 Levels of Conformance

Conformance may be classified into levels:

#### Basic Conformance
- supports Onto message structure
- validates schema
- produces structured results

#### Intermediate Conformance
- enforces permissions and risk constraints
- handles error categories
- maintains execution consistency

#### Full Conformance
- implements delegation model
- enforces trust model
- ensures traceability and auditability
- integrates human review mechanisms

---

### 11.3 Compliance Verification

Compliance may be verified by:

- schema validation
- execution testing
- audit of outcomes and error handling

---

### 11.4 Non-Conformance

A system is non-compliant if it:

- ignores required fields
- bypasses constraints
- produces undefined or inconsistent results

Non-compliant systems must not be considered reliable within Onto-based architectures.