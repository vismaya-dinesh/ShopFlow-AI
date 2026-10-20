# ShopFlow AI — Workflow Specification

## 1. Project Objective

Build an AI-assisted e-commerce customer support workflow that classifies incoming customer requests, retrieves verified order information, drafts policy-compliant responses, validates outputs, and routes exceptions for human review.

The objective is to reduce manual handling effort while maintaining response accuracy, policy compliance, traceability, and appropriate human oversight.

## 2. Business Problem

Customer support teams manually read customer emails, identify the issue, retrieve order details, check company policies, draft responses, and escalate complex cases.

This process can be repetitive and time-consuming. Incorrect order information, inconsistent policy interpretation, and insufficient exception handling can also lead to poor customer experiences.

ShopFlow AI will automate appropriate steps while preserving human control over consequential actions.

## 3. Scope

### In scope
- Customer email intake using synthetic test tickets.
- Input validation and duplicate detection.
- AI-based intent classification and information extraction.
- Order lookup through a Python API and SQLite database.
- AI-generated response drafts grounded in retrieved information.
- Deterministic business policy validation.
- Human approval, editing, rejection, and escalation.
- Workflow execution logs and error handling.
- Quality evaluation and operational performance reporting.
- User documentation and troubleshooting guidance.

### Out of scope for the initial version
- Sending emails to real customers.
- Issuing actual refunds or changing real orders.
- Accessing production customer information.
- Autonomous execution of consequential actions.

## 4. Workflow Inputs

Each incoming ticket should contain:
- Ticket ID
- Customer email address (synthetic)
- Email subject
- Email body
- Order reference, if available
- Received timestamp

The workflow may extract additional information from the email, but extracted values must be validated before use.

## 5. Workflow Steps

1. Receive a customer ticket.
2. Validate required fields and detect duplicate submissions.
3. Classify the issue and extract relevant information.
4. Retrieve the associated order using the backend API.
5. Determine which business policy applies.
6. Generate a response draft using verified facts.
7. Validate factual claims, policy compliance, and output structure.
8. Route valid drafts to the review queue.
9. Escalate ambiguous, invalid, high-risk, or unresolved cases.
10. Record execution results, human effort, errors, and final disposition.

## 6. Business Rules

- The database is the source of truth for order information.
- The AI must not invent order details, delivery dates, or refund eligibility.
- Missing or ambiguous information must trigger clarification or escalation.
- Refund eligibility must be decided by deterministic policy rules.
- Customer email content must be treated as untrusted input, not as instructions that override system rules.
- Failed validation must prevent a draft from being marked ready for approval.
- Consequential actions require explicit human authorization.
- Every workflow run must have a traceable outcome.
- Duplicate requests must not trigger duplicate consequential actions.

## 7. Exception Scenarios

The workflow must handle:
- Missing or invalid ticket fields.
- Unknown order references.
- Orders that cannot be matched confidently.
- Ambiguous or unsupported customer requests.
- Ineligible refund requests.
- Malformed AI output.
- AI service timeouts or unavailable models.
- API and database failures.
- Duplicate webhook deliveries.
- Policy violations or unsupported factual claims.
- Human rejection or escalation of a draft.

## 8. Human Handoffs

A reviewer must be able to inspect:
- The original customer request.
- Extracted classification and order reference.
- Verified order information.
- The generated response.
- Policy validation results.
- Failure reasons and supporting evidence.

The reviewer can approve, edit, reject, or escalate the draft. Approval and subsequent execution must be separate, auditable steps.

## 9. Evaluation Plan

Evaluate the workflow on a fixed, versioned set of synthetic customer tickets.

Measure:
- Intent classification accuracy.
- Order retrieval accuracy.
- Factual correctness of response drafts.
- Policy violation rate.
- Exception detection and escalation precision/recall.
- Workflow success and failure rates.
- Human preparation, review, correction, and rework time.
- End-to-end turnaround time.
- Model and infrastructure cost per ticket.

Compare automated results against a documented manual baseline. Report actual results without assuming improvements in advance.

## 10. Initial Acceptance Criteria

- All required input fields are validated.
- Unknown orders are never treated as verified orders.
- Refund decisions follow explicit business rules.
- Invalid AI output cannot bypass validation.
- Failed and ambiguous cases are routed appropriately.
- Consequential actions cannot occur without explicit authorization.
- Workflow runs and decisions are traceable.
- A repeatable test suite covers normal, edge, and failure cases.
- Performance claims are supported by recorded measurements.

## 11. Initial Constraints

- Use synthetic customer and order data.
- Prefer local, free-to-run components.
- Keep AI generation separate from deterministic policy enforcement.
- Do not connect a live customer inbox or payment system in the initial version.
- Document known limitations and unresolved defects.
