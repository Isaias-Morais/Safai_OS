# Requirements Traceability

| Requirement group | Owner | Status | Acceptance / test |
|---|---|---|---|
| Central auth and role authorization | Backend + Shared | DATABASE FOUNDATION IMPLEMENTED; AUTH FLOW NOT STARTED | RLS role/ownership tests and trusted-command tests |
| Citizen reporting, map confirmation, tracking, feedback | Citizen + Backend | NOT STARTED | Auth, validation, lifecycle integration tests |
| Admin review, assignment, verification, moderation | Admin + Backend | NOT STARTED | Role/transition/audit tests |
| Driver assigned work and cleanup evidence | Driver + Backend | NOT STARTED | Assignment-isolation tests |
| Incident lifecycle, verification, audit | Backend | ARCHITECTURE SIGNED OFF | Orthogonal-status transition matrix, command authorization, seven-day expiry, self-verification denial, history, and idempotency tests |
| Duplicate assessment | Backend + Admin | ARCHITECTURE SIGNED OFF | Admin-review, preservation, and no-automatic-closure tests; thresholds/merge policy pending |
| Data model, RLS, storage isolation | Backend + Shared | MIGRATION AND TESTS AUTHORED; LOCAL EXECUTION PENDING DOCKER | Foreign-key/uniqueness tests, RLS denial tests, private-object access tests |
| Safai Coins ledger/redemption | Backend | BLOCKED | Requires reward and utility rules |
| E002 detector contract | AI/Detector | IN PROGRESS | Hash, schema, timeout, inference tests |
| Gemma contextual reasoning | AI/Reasoning | DEFERRED | Provider/schema/safety review |
| Benchmark evidence | ML repository | TESTED | Separate locked/India reports preserved |
| Export, production observability, field validation | AI/Detector + Backend | NOT STARTED | Deployment/load/field tests |

Approved architecture policy: the reporter may verify cleanup performed by an assigned driver; no cleanup performer may verify their own cleanup; a reporter who performed cleanup requires authorized Admin verification. Citizen approval and authorized Admin approval close the incident and invoke the same idempotent, auditable reward path. Evidence submission alone never rewards. Admin evidence rejection enters `RESOLUTION_REQUIRED`, records a reason, and retains history.

Proposed, not approved business policy: Admin reassigning, requesting rework, escalating, or permitted auditable cancellation after rejection.

Open decisions must not be treated as implemented: duplicate thresholds, merge/closure rules; coin amount/formula, redemption conversion and bounds, expiry, refund/reversal policy, payment/utility provider and electricity integration; driver onboarding/availability; account invitation/recovery; SUPERADMIN governance; data/image retention and legal privacy; notification and maps providers; cancellation/escalation policy; and production monitoring/operational requirements.
