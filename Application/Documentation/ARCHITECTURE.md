# Application Architecture

Recommended foundation: a single TypeScript web application (Next.js) with a server-side API boundary, Supabase Auth/Postgres/Storage, and the existing Python detector deployed as an internal inference service. This minimizes duplicated business logic while keeping GPU dependencies out of the web runtime.

`Citizen/Admin/Driver UI → server API → workflow + RLS-protected data/storage → detector adapter → E002 Python service`.

Supabase is a proposed platform, not configured in this repository. Before implementation, validate current provider guidance, pin dependencies, enable RLS on exposed tables, use ownership predicates in policies, store authorization in backend-controlled app metadata/tables rather than user-editable metadata, and keep service-role credentials server-only.

The backend owns incident transitions and calls AI adapters. Frontends render authorized data only. A queue/background worker is required for seven-day verification deadlines, retries, image processing, and notifications.

## Incident lifecycle and state ownership

The lifecycle must not use one overloaded status column. AI analysis, duplicate screening, assignment, evidence, verification, and rewards are separate facts with their own history. The backend is the only transition authority; clients request commands, never write status directly.

The corrected incident flow is:

`DRAFT (citizen report + AI analysis + citizen review) → SUBMITTED → duplicate detection → ADMIN_REVIEW → ASSIGNED → CLEANUP_IN_PROGRESS → evidence submitted → AWAITING_CITIZEN_VERIFICATION`.

The reporting citizen may verify evidence submitted by an assigned driver. From citizen verification, `APPROVED → CLOSED → idempotent reward creation`; `DENIED → AWAITING_ADMIN_REVIEW`; and no response within seven days also leads to `AWAITING_ADMIN_REVIEW`. An authorized Admin approval closes the incident and permits the same idempotent reward action. A person who performed the cleanup may never verify that cleanup, regardless of any other role; if the reporter is the cleanup performer, an authorized Admin must handle verification.

When an authorized Admin rejects submitted cleanup evidence, the incident enters `RESOLUTION_REQUIRED` and the rejection reason is recorded. Reassigning a driver, requesting rework, escalating, or cancelling with an auditable reason are proposed resolution actions that require final business-policy approval. They must preserve prior assignment, evidence, decision, and audit history; rework never overwrites prior evidence. Admin review is not a mandatory stage after citizen approval.

Suggested independent state fields are:

| Concern | Owner | Suggested values |
|---|---|---|
| `incidents.lifecycle_status` | Backend | `DRAFT`, `SUBMITTED`, `ADMIN_REVIEW`, `ASSIGNED`, `CLEANUP_IN_PROGRESS`, `AWAITING_CITIZEN_VERIFICATION`, `AWAITING_ADMIN_REVIEW`, `RESOLUTION_REQUIRED`, `CLOSED` |
| `duplicate_assessments.status` | Backend/Admin | `NOT_RUN`, `POTENTIAL_MATCH`, `CLEARED`, `CONFIRMED_DUPLICATE` (final merge/closure policy remains open) |
| `driver_assignments.status` | Backend/assigned driver | `ASSIGNED`, `ACCEPTED`, `EN_ROUTE`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED` |
| `cleanup_evidence.status` | Backend/Admin | `SUBMITTED`, `ACCEPTED`, `REJECTED`; rejection reason is retained |
| `verification_decisions.status` | eligible verifier/Admin | `PENDING`, `APPROVED`, `DENIED`, `EXPIRED` |
| `safai_coin_transactions.status` | Backend only | ledger posting state; credit amount, reversal, expiry, redemption, and utility rules are intentionally undecided |

The backend must enforce verifier eligibility, not merely hide UI controls: the reporting citizen may approve or deny an assigned driver's cleanup; the cleanup performer is always disqualified; and a reporter who performed the cleanup is routed to an authorized Admin verifier.

## Duplicate assessment and reward boundaries

Duplicate detection creates an assessment, never an automatic closure. It may consider location, time, image similarity, waste category, and incident context, but spatial proximity alone is insufficient. Potential matches are available to authorized Admins for review. Original incident records, reporter ownership, media, and audit history remain preserved; no AI similarity score alone may merge, delete, or close an incident. Duplicate thresholds, merge rules, and any closure policy remain pending product-owner approval.

Safai Coins are created only after an authorized closure through citizen approval or authorized Admin approval. Driver evidence submission never creates a reward. Reward creation must be transactional, idempotent, auditable, and derived from the ledger, with a unique reward source/idempotency constraint to prevent duplicate credits. Coin amounts, formulas, expiry, conversion, redemption limits, reversal/refund policy, and electricity-utility integration are intentionally unresolved.

## Proposed data model

| Entity | Purpose and important fields | Keys, relationships, ownership, and constraints |
|---|---|---|
| `profiles` | Application identity: display name, contact preferences, account state. | PK/FK `user_id → auth.users`; user reads/updates only allowed profile fields. Unique `user_id`; never use client-editable profile data as authority. |
| `user_roles` and `admin_permissions` | Backend-controlled role grants and optional administrative scopes. | PK UUID; FK to `profiles`; unique active role grant per user/role/scope. Only `SUPERADMIN` workflow may change grants; normal users have no write path. |
| `incidents` | Report location, narrative, lifecycle status, reporter, timestamps, chosen resolution. | PK UUID; FK `reporter_id → profiles`; index `(reporter_id, created_at DESC)` and `(lifecycle_status, updated_at)`. Reporter owns the report; driver access derives from current assignment; admin access derives from permission. |
| `incident_media` | Original report photographs and secure storage metadata. | PK UUID; FK `incident_id`; uploader FK `profiles`; unique storage object key and content hash index. Private objects only; access derives from incident authorization. |
| `ai_analysis_results` | Detector invocation metadata, E002 checkpoint hash, detections, optional separate reasoning result. | PK UUID; FK `incident_id`; immutable result payload/version fields; index `(incident_id, created_at DESC)`. Server writes only; YOLO output and Gemma reasoning must remain distinguishable. |
| `duplicate_assessments` | Candidate incident match, rule/model version, reviewer outcome. | PK UUID; FKs to source and candidate `incidents`; unique `(incident_id, candidate_incident_id, assessment_version)`. Backend/Admin write only. |
| `driver_assignments` | Assignment history, driver, status, assigned/accepted/completed times. | PK UUID; FKs `incident_id`, `driver_id`; index `(driver_id, status, assigned_at DESC)`. Enforce at most one active assignment per incident; driver sees only own assignments. |
| `cleanup_evidence` | Driver’s cleanup media, statement, submitter, review state. | PK UUID; FK `incident_id`, `assignment_id`, `submitted_by`; index `(incident_id, submitted_at DESC)`. Submitter must be currently assigned driver; evidence media uses a child table or typed `incident_media` relation. |
| `verification_decisions` | Citizen/admin decision, actor, decision time, reason, expiry context. | PK UUID; FK `incident_id`, optional `cleanup_evidence_id`, `decided_by`; unique active verification request per evidence. Decision is append-only and eligibility is checked server-side. |
| `citizen_feedback` | Post-resolution feedback distinct from verification. | PK UUID; FK `incident_id`, `author_id`; unique `(incident_id, author_id)` if one response is intended. Author sees own feedback; authorized staff see moderation view. |
| `safai_coin_accounts` | One balance-bearing account per eligible user. | PK UUID; FK `owner_id`; unique `owner_id`. User reads own account; all balance mutation is backend controlled. |
| `safai_coin_transactions` | Append-only credit/debit/reversal ledger with source and idempotency key. | PK UUID; FK `account_id`, optional `incident_id`; unique immutable idempotency key and unique reward source once business policy defines it. Server writes only; no amount/formula is specified here. |
| `audit_logs` | Append-only security/workflow record: actor, action, entity, before/after, request ID, timestamp. | PK UUID; actor FK nullable for system actions; indexes `(entity_type, entity_id, created_at)` and `(actor_id, created_at)`. Ordinary users cannot insert, update, or delete. |
| `notifications` | Recipient, template/event, delivery state, read time. | PK UUID; FK `recipient_id`, optional `incident_id`; index `(recipient_id, read_at, created_at DESC)`. Recipient reads/marks own notifications; server creates and delivers. |
