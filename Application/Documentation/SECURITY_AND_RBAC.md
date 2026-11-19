# Security and RBAC

Authentication establishes identity; a role selection screen never grants authority. Every protected operation rechecks identity, backend-controlled role, assignment, and incident-state transition server-side. Supabase Auth identity alone is not authorization, and client-editable user metadata must not be used for roles or permissions.

Citizen: own profile/reports, permitted evidence review, feedback, and read-only nearby incidents with privacy filtering. The reporting citizen may approve or deny cleanup performed by their assigned driver. Driver: only assigned incidents and evidence/status submission. Admin: role-scoped review; `VIEWER` is read-only, `ADMIN` operational, `SUPERADMIN` manages administrative access. A cleanup performer cannot verify their own cleanup regardless of role; if the reporter is that performer, an authorized Admin verifies instead. No client user may issue or alter rewards.

Use private object storage with signed, short-lived access; strip unsafe metadata; record upload identity and content hash. Audit immutable actor/time/action/before/after context. Apply rate limits, duplicate/abuse review, least privilege, server-side timestamps in IST, and idempotency keys for incident submission, evidence decisions, and ledger entries.

## Required RLS and backend authorization controls

Enable RLS on every exposed application table and storage object. `TO authenticated` is not enough: each policy must use an ownership, assignment, or backend-controlled role predicate. Service-role credentials remain server-only; security-definer functions, if used, must use a fixed `search_path`, minimal privileges, and explicit input authorization.

| Resource | Required database/RLS rule | Required backend command checks |
|---|---|---|
| Profiles | A user can select their profile and update only approved self-service fields. | No endpoint may let a user change roles, admin scope, account state, or another profile. |
| Roles and permissions | No ordinary client insert/update/delete; grants are readable only as necessary for the current user. | Only `SUPERADMIN` grant/revoke workflow; audit every change and prevent self-escalation. |
| Incidents and media | Reporter accesses own incident/media; assigned driver accesses only active assigned work; admin access requires scoped role. Storage access must use matching private-object predicates/signed URLs. | Validate reporter, visibility/redaction rules, media ownership/hash, and every lifecycle transition. |
| Assignments and evidence | Driver can read only own assignments and create evidence only for an active assignment; no direct assignment creation. | Admin assignment command validates availability/state; evidence command validates current assignment and records actor/time. |
| Verification and feedback | Reporter may access the assigned driver's requested evidence; the cleanup performer is excluded; decisions cannot be overwritten. | Recheck pending verification, seven-day deadline, reporter/cleanup-performer identities, Admin role where required, and legal transition. |
| Coins account and ledger | Owner may read own account/ledger; no ordinary client writes. | Closure command creates reward through one transactional, idempotent operation; no driver or citizen may issue/alter rewards. |
| Audit logs | No ordinary client writes, updates, or deletes; privileged read is tightly scoped. | Every mutating command writes an audit event in the same transaction where possible. |
| Notifications | Recipient can read/mark only their own notifications; creation/delivery is server-only. | Verify recipient authorization before exposing incident details in notification payloads. |

`VIEWER` must be read-only, `ADMIN` may exercise only documented operational commands, and `SUPERADMIN` alone manages administrative grants. Database constraints are a second line of defense: active-assignment uniqueness, append-only decision/ledger/audit records, foreign keys, request idempotency, and transactionally coupled incident closure plus reward creation.

Admin evidence rejection must record a reason and retain all evidence/assignment history. Reassignment, rework, escalation, and permitted cancellation are proposed administrative actions awaiting final business-policy approval; each must be authorized, audited, and transition through `RESOLUTION_REQUIRED`.

Open decisions: account provisioning/invitation/recovery, driver onboarding/availability, admin-governance process, retention policy, map provider, notification channel/delivery policy, duplicate thresholds/merge policy, coin redemption policy, electricity integration, cancellation/escalation policy, and production operational requirements.
