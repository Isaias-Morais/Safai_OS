# SafaiOS Database Foundation

## Scope

The version-controlled Supabase database foundation is under `supabase/`. It establishes the signed-off entities, PostgreSQL constraints, RLS, private storage buckets, database guardrails, and pgTAP tests. It does not implement an application UI, authentication flow, server command handlers, reward formula, duplicate threshold, or remote deployment.

## Local setup

Prerequisites: Docker Desktop with its Linux engine running, the Supabase CLI, and a supported local PostgreSQL 17 Supabase stack.

```powershell
supabase start
supabase db reset
supabase test db
supabase db lint --level error --fail-on error
```

`supabase db reset` applies every file in `supabase/migrations/` to the local database only. pgTAP tests in `supabase/tests/` are transactional and are rolled back after each test file.

## Remote safety

The confirmed Safai_OS remote project is intentionally not linked or migrated by this foundation. Before a remote migration, inspect its migration history and schema, confirm the target environment, review the migration, and obtain explicit product-owner approval. Do not run `supabase db push`, `supabase db reset --linked`, or any destructive remote operation without that approval.

## Environment variables

Copy `.env.example` to an ignored local environment file or configure equivalent deployment secrets. `SUPABASE_PUBLISHABLE_KEY` may be used by a browser client only with RLS enabled. `SUPABASE_SECRET_KEY`, database passwords, Gemini credentials, and OAuth client secrets are server-only and must never use a public environment-variable prefix.

## Database boundary

The migration defines the 15 signed-off entities and the supporting `cleanup_evidence_media` relation. It uses independent incident, assignment, evidence, verification, duplicate, and ledger status types. The backend command layer remains responsible for legal lifecycle transitions, seven-day scheduling, administrative permission scopes, and transactional close-and-reward behavior.

RLS permits only narrowly scoped direct operations: citizens may create their own drafts and read their authorized records; assigned drivers may submit evidence for their active assignment; eligible reporters may submit a verification decision; and recipients may mark their notifications read. Protected mutations—including roles, lifecycle transitions, AI results, reward ledger entries, audit records, assignment management, and administrative decisions—require a trusted server-side operation.

## Storage

`incident-media` and `cleanup-evidence` are private buckets. Browser uploads require a user-scoped object path and owner. Reads require object ownership, a corresponding authorized incident relation, or an authorized administrative role. Application code should use short-lived signed URLs after server-side authorization; it must not make either bucket public.

## Testing

`supabase/tests/database_foundation.test_test.sql` exercises schema objects, active-assignment uniqueness, RLS isolation for citizens and drivers, protected AI/role/reward/audit operations, reporter verification, self-verification denial, Viewer/Admin limits, and storage isolation. The CI `database` job runs the local stack and this suite without production credentials.
