# SafaiOS Final Architecture Sign-off

## A. Architecture status

The documented application architecture is internally consistent at the foundation level. It is ready for staged implementation of the shared security, data, and workflow foundation, provided implementation begins with the prerequisites below and does not assume unresolved business rules are decided. No application runtime, database schema, or deployment configuration exists yet.

There is no blocker to documenting the core workflow. Capabilities that depend on unresolved product policy—duplicate merge/closure, rewards redemption, electricity integration, cancellation/escalation, provider choices, and retention—must remain out of scope until approved.

## B. Approved product and technical decisions

- The application layer consumes, but does not copy or modify, the existing E002 Python detector.
- Business workflow is server-authoritative; clients request commands and never write protected statuses, roles, balances, or audit fields directly.
- Incident lifecycle, driver assignment, cleanup evidence, verification decision, duplicate assessment, and reward transaction are independent records/statuses with retained history.
- The reporting citizen may approve or deny cleanup evidence submitted by an assigned driver.
- A cleanup performer may never verify their own cleanup, regardless of other roles. If the reporter performed the cleanup, an authorized Admin verifies it.
- Citizen approval closes the incident and invokes an idempotent, auditable reward transaction. Citizen denial and no response within seven days move the incident to `AWAITING_ADMIN_REVIEW`.
- Authorized Admin approval is the other closure path and invokes the same reward process.
- Submitted driver evidence alone cannot generate a reward.
- Duplicate detection creates an assessment; it does not automatically merge, delete, close, or otherwise resolve an incident. Spatial proximity alone is insufficient.
- RLS, private storage, server-side role/ownership/assignment checks, immutable audit records, and server-only privileged credentials are required before exposing application data.

## C. Proposed decisions

The following are recommendations, not approved business rules:

- After an Admin rejects cleanup evidence and records a reason, use `RESOLUTION_REQUIRED` as the workflow state.
- Permit authorized Admin commands to reassign a driver, request rework, escalate, or cancel with an auditable reason where cancellation is allowed.
- Preserve all prior evidence, assignments, decisions, and audit events during rework or reassignment.
- Use a queue/background worker for seven-day deadlines, retries, image processing, and notifications.
- Use a single server-side application boundary with private storage and the existing detector as an internal service.

## D. Unresolved decisions

| Area | Decision requiring product-owner approval |
|---|---|
| Accounts | Invitation, provisioning, recovery, and account-state policy. |
| Drivers | Onboarding, eligibility, availability, service areas, and reassignment rules. |
| Administration | `SUPERADMIN` governance, grant/revocation process, separation of duties, and operational scopes. |
| Privacy and retention | Legal basis, data and image/evidence retention, deletion, export, and access-review policy. |
| Notifications | Provider, channels, delivery/retry rules, consent, and message retention. |
| Maps/geolocation | Provider, precision, consent, retention, and fallback behavior. |
| Duplicates | Assessment thresholds, reviewer workflow, merge semantics, and any permitted closure policy. |
| Safai Coins | Amounts, earning formula, expiry, conversion, redemption limits, refunds/reversals, and ledger business rules. |
| Electricity integration | Provider, eligibility, identity matching, settlement, reconciliation, and failure handling. |
| Resolution | Final cancellation and escalation policy, including when each action is permitted. |
| Operations | SLOs, monitoring, alerting, incident response, backup/recovery, capacity, and field-validation requirements. |

## E. Lifecycle verification

```text
DRAFT (report, E002 analysis, citizen review)
  → SUBMITTED
  → duplicate assessment (recorded; no automatic closure)
  → ADMIN_REVIEW
  → ASSIGNED
  → CLEANUP_IN_PROGRESS
  → evidence submitted
  → AWAITING_CITIZEN_VERIFICATION

citizen approval by eligible reporter → CLOSED → idempotent Safai Coins transaction
citizen denial                       → AWAITING_ADMIN_REVIEW
no response after seven days         → AWAITING_ADMIN_REVIEW
authorized Admin approval            → CLOSED → same idempotent reward transaction
Admin evidence rejection             → RESOLUTION_REQUIRED (reason retained)
```

The cleanup performer is ineligible to verify that cleanup. When the reporter is the cleanup performer, an authorized Admin performs verification. Admin review does not occur after a valid citizen approval. Proposed actions from `RESOLUTION_REQUIRED` are reassign, rework, escalate, or permitted auditable cancellation; none may discard history.

## F. Entity and relationship verification

The documented model consistently assigns responsibility to `profiles`; backend-controlled `user_roles` and `admin_permissions`; `incidents`; `incident_media`; immutable `ai_analysis_results`; `duplicate_assessments`; historical `driver_assignments`; `cleanup_evidence`; append-only `verification_decisions`; `citizen_feedback`; `safai_coin_accounts` and append-only `safai_coin_transactions`; `audit_logs`; and `notifications`.

An incident is reported by one profile, has media and analysis results, may have duplicate assessments and an assignment history, and has evidence/verification history. Rewards reference the eligible account and incident through an idempotent ledger source. Media, assignments, evidence, decisions, ledger activity, and audit records remain retained rather than overwritten by rework.

## G. Security verification

- Identity is not authority: role selection and client-editable metadata never grant permissions.
- RLS must use ownership, assignment, and backend-controlled role predicates; `TO authenticated` alone is insufficient.
- Citizens access their own reports and the assigned-driver evidence they are eligible to verify. Drivers access only active assignments. `VIEWER` is read-only, `ADMIN` is operationally scoped, and `SUPERADMIN` controls administrative grants.
- Server commands recheck state, actor identity, role, assignment, deadline, and cleanup-performer conflict before transitions.
- Storage is private; access is authorized through short-lived signed access and matching incident authorization.
- Ordinary users cannot create, mutate, or delete roles, ledger entries, or audit records. Rewards are transactional, idempotent, and created only at authorized closure.

## H. ML integration verification

The integration contract matches the existing E002 assets and source:

- Checkpoint: `runs/detect/runs/detect/runs/safaios/safaios_yolo11s_v10k_img768/weights/best.pt`
- SHA-256: `8bd30b05a0b4a84d95c5e71f213b967d255144a8fe57791ef110b920fc86d073`
- Configuration: 768px, confidence `0.25`, NMS IoU `0.60`; matching IoU `0.50` remains evaluation-only.
- Taxonomy: `plastic_bottle`, `plastic_wrapper_bag`, `paper_cardboard`, `glass_bottle_container`, and `metal_can`.
- `YOLOInferenceEngine.predict` returns normalized `Prediction` values, which map to the existing detection API schemas without semantic change.
- E002 detection is server-side object evidence only. Future Gemma reasoning is a separate, reviewable suggestion layer and cannot authorize workflow actions or override YOLO/workflow controls.

No model was retrained, exported, copied, or modified for this sign-off.

## I. Implementation readiness

| Prerequisite | Status |
|---|---|
| Architecture boundaries and core lifecycle | Signed off |
| Verification/self-verification policy | Signed off |
| E002 identity and inference schema reference | Verified against repository source |
| Database schema, migrations, RLS, storage policies | Not started |
| Authentication/session implementation | Not started |
| Workflow/API implementation and audit ledger | Not started |
| Exact duplicate, reward-redemption, provider, retention, cancellation, and operations policies | Product-owner decision required |
| Production monitoring, security/load tests, and field validation | Not started |

## J. Recommended implementation sequence

1. Approve the unresolved decisions needed for the first release scope; keep other capabilities explicitly deferred.
2. Select and pin the application stack, establish secrets handling, and implement authenticated identity plus backend-controlled role grants.
3. Create the data schema, RLS/private-storage policies, audit foundation, and automated authorization/constraint tests.
4. Implement server-side incident commands, assignment/evidence history, seven-day verification scheduling, and transactional reward idempotency.
5. Implement the existing E002 inference adapter and authenticated draft-analysis path without duplicating weights or inference logic.
6. Build Citizen reporting/tracking and verification, then Admin review/assignment, then Driver execution/evidence against the same commands.
7. Add notifications, observability, security/load testing, operational controls, and field validation before any production claim.
