begin;

-- SafaiOS Phase 1 database foundation. Application workflow commands remain
-- server-side; this migration establishes durable data, RLS, and guardrails.

create extension if not exists pgcrypto;

create type public.app_role as enum ('CITIZEN', 'DRIVER', 'ADMIN', 'VIEWER', 'SUPERADMIN');
create type public.account_status as enum ('ACTIVE', 'SUSPENDED', 'DEACTIVATED');
create type public.incident_lifecycle_status as enum (
  'DRAFT', 'SUBMITTED', 'ADMIN_REVIEW', 'ASSIGNED', 'CLEANUP_IN_PROGRESS',
  'AWAITING_CITIZEN_VERIFICATION', 'AWAITING_ADMIN_REVIEW',
  'RESOLUTION_REQUIRED', 'CLOSED'
);
create type public.media_kind as enum ('REPORT', 'CLEANUP');
create type public.ai_analysis_status as enum ('PENDING', 'COMPLETED', 'FAILED');
create type public.duplicate_assessment_status as enum ('NOT_RUN', 'POTENTIAL_MATCH', 'CLEARED', 'CONFIRMED_DUPLICATE');
create type public.driver_assignment_status as enum ('ASSIGNED', 'ACCEPTED', 'EN_ROUTE', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
create type public.cleanup_evidence_status as enum ('SUBMITTED', 'ACCEPTED', 'REJECTED');
create type public.verification_status as enum ('PENDING', 'APPROVED', 'DENIED', 'EXPIRED');
create type public.verification_actor_kind as enum ('CITIZEN', 'ADMIN', 'SYSTEM');
create type public.coin_transaction_type as enum ('REWARD_CREDIT', 'REDEMPTION_DEBIT', 'ADJUSTMENT', 'REVERSAL');
create type public.coin_transaction_status as enum ('POSTED', 'VOIDED');
create type public.notification_status as enum ('PENDING', 'SENT', 'FAILED', 'READ');

create table public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  contact_preferences jsonb not null default '{}'::jsonb,
  account_status public.account_status not null default 'ACTIVE',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.user_roles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(user_id) on delete cascade,
  role public.app_role not null,
  granted_by uuid references public.profiles(user_id) on delete set null,
  granted_at timestamptz not null default now(),
  revoked_at timestamptz,
  revocation_reason text,
  check ((revoked_at is null and revocation_reason is null) or revoked_at is not null)
);
create unique index user_roles_one_active_role_per_user_idx
  on public.user_roles (user_id, role) where revoked_at is null;

create table public.admin_permissions (
  id uuid primary key default gen_random_uuid(),
  admin_user_id uuid not null references public.profiles(user_id) on delete cascade,
  permission_key text not null check (permission_key ~ '^[A-Z][A-Z0-9_]{2,99}$'),
  granted_by uuid references public.profiles(user_id) on delete set null,
  granted_at timestamptz not null default now(),
  revoked_at timestamptz,
  revocation_reason text
);
create unique index admin_permissions_one_active_permission_idx
  on public.admin_permissions (admin_user_id, permission_key) where revoked_at is null;

create table public.incidents (
  id uuid primary key default gen_random_uuid(),
  reporter_id uuid not null references public.profiles(user_id) on delete restrict,
  title text not null check (char_length(title) between 1 and 200),
  description text not null check (char_length(description) between 1 and 5000),
  latitude numeric(9,6) check (latitude between -90 and 90),
  longitude numeric(9,6) check (longitude between -180 and 180),
  lifecycle_status public.incident_lifecycle_status not null default 'DRAFT',
  submitted_at timestamptz,
  citizen_verification_due_at timestamptz,
  closed_at timestamptz,
  resolution_note text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check ((latitude is null and longitude is null) or (latitude is not null and longitude is not null)),
  check ((lifecycle_status <> 'CLOSED') or closed_at is not null)
);
create index incidents_reporter_created_idx on public.incidents (reporter_id, created_at desc);
create index incidents_lifecycle_updated_idx on public.incidents (lifecycle_status, updated_at desc);

create table public.incident_media (
  id uuid primary key default gen_random_uuid(),
  incident_id uuid not null references public.incidents(id) on delete cascade,
  uploaded_by uuid not null references public.profiles(user_id) on delete restrict,
  media_kind public.media_kind not null,
  storage_bucket text not null check (storage_bucket in ('incident-media', 'cleanup-evidence')),
  object_path text not null check (char_length(object_path) between 1 and 1024),
  content_type text not null check (content_type in ('image/jpeg', 'image/png')),
  byte_size bigint not null check (byte_size > 0),
  content_sha256 text not null check (content_sha256 ~ '^[A-Fa-f0-9]{64}$'),
  created_at timestamptz not null default now(),
  unique (storage_bucket, object_path)
);
create index incident_media_incident_created_idx on public.incident_media (incident_id, created_at desc);
create index incident_media_content_sha256_idx on public.incident_media (content_sha256);

create table public.ai_analysis_results (
  id uuid primary key default gen_random_uuid(),
  incident_id uuid not null references public.incidents(id) on delete cascade,
  media_id uuid references public.incident_media(id) on delete set null,
  analysis_status public.ai_analysis_status not null default 'PENDING',
  detector_name text not null default 'E002 YOLO11s',
  checkpoint_sha256 text not null check (checkpoint_sha256 ~ '^[A-Fa-f0-9]{64}$'),
  detector_config jsonb not null default '{}'::jsonb,
  detections jsonb not null default '[]'::jsonb,
  reasoning_result jsonb,
  error_code text,
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  check ((analysis_status = 'FAILED') = (error_code is not null))
);
create index ai_analysis_results_incident_created_idx on public.ai_analysis_results (incident_id, created_at desc);

create table public.duplicate_assessments (
  id uuid primary key default gen_random_uuid(),
  incident_id uuid not null references public.incidents(id) on delete cascade,
  candidate_incident_id uuid not null references public.incidents(id) on delete cascade,
  assessment_version text not null,
  status public.duplicate_assessment_status not null default 'NOT_RUN',
  assessment_evidence jsonb not null default '{}'::jsonb,
  reviewed_by uuid references public.profiles(user_id) on delete set null,
  reviewed_at timestamptz,
  review_note text,
  created_at timestamptz not null default now(),
  check (incident_id <> candidate_incident_id),
  check ((reviewed_by is null) = (reviewed_at is null))
);
create unique index duplicate_assessments_pair_version_idx
  on public.duplicate_assessments (least(incident_id, candidate_incident_id), greatest(incident_id, candidate_incident_id), assessment_version);
create index duplicate_assessments_incident_status_idx on public.duplicate_assessments (incident_id, status, created_at desc);

create table public.driver_assignments (
  id uuid primary key default gen_random_uuid(),
  incident_id uuid not null references public.incidents(id) on delete restrict,
  driver_id uuid not null references public.profiles(user_id) on delete restrict,
  status public.driver_assignment_status not null default 'ASSIGNED',
  assigned_by uuid references public.profiles(user_id) on delete set null,
  assigned_at timestamptz not null default now(),
  accepted_at timestamptz,
  completed_at timestamptz,
  cancelled_at timestamptz,
  cancellation_reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check ((status <> 'CANCELLED') or cancelled_at is not null),
  check ((status <> 'COMPLETED') or completed_at is not null)
);
create unique index driver_assignments_one_active_incident_idx
  on public.driver_assignments (incident_id)
  where status in ('ASSIGNED', 'ACCEPTED', 'EN_ROUTE', 'IN_PROGRESS');
create index driver_assignments_driver_status_assigned_idx
  on public.driver_assignments (driver_id, status, assigned_at desc);

create table public.cleanup_evidence (
  id uuid primary key default gen_random_uuid(),
  incident_id uuid not null references public.incidents(id) on delete restrict,
  assignment_id uuid not null references public.driver_assignments(id) on delete restrict,
  submitted_by uuid not null references public.profiles(user_id) on delete restrict,
  statement text check (char_length(statement) <= 5000),
  status public.cleanup_evidence_status not null default 'SUBMITTED',
  reviewed_by uuid references public.profiles(user_id) on delete set null,
  reviewed_at timestamptz,
  rejection_reason text,
  submitted_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  check ((status = 'REJECTED') = (rejection_reason is not null)),
  check ((reviewed_by is null) = (reviewed_at is null))
);
create index cleanup_evidence_incident_submitted_idx on public.cleanup_evidence (incident_id, submitted_at desc);
create index cleanup_evidence_assignment_idx on public.cleanup_evidence (assignment_id, submitted_at desc);

create table public.cleanup_evidence_media (
  evidence_id uuid not null references public.cleanup_evidence(id) on delete cascade,
  media_id uuid not null references public.incident_media(id) on delete restrict,
  created_at timestamptz not null default now(),
  primary key (evidence_id, media_id)
);

create table public.verification_decisions (
  id uuid primary key default gen_random_uuid(),
  incident_id uuid not null references public.incidents(id) on delete restrict,
  cleanup_evidence_id uuid not null references public.cleanup_evidence(id) on delete restrict,
  status public.verification_status not null default 'PENDING',
  actor_kind public.verification_actor_kind not null default 'SYSTEM',
  decided_by uuid references public.profiles(user_id) on delete restrict,
  reason text,
  due_at timestamptz,
  decided_at timestamptz,
  created_at timestamptz not null default now(),
  check (
    (status = 'PENDING' and decided_by is null and decided_at is null and actor_kind = 'SYSTEM') or
    (status = 'EXPIRED' and decided_by is null and decided_at is not null and actor_kind = 'SYSTEM') or
    (status in ('APPROVED', 'DENIED') and decided_by is not null and decided_at is not null and actor_kind in ('CITIZEN', 'ADMIN'))
  )
);
create unique index verification_decisions_one_pending_per_evidence_idx
  on public.verification_decisions (cleanup_evidence_id) where status = 'PENDING';
create index verification_decisions_incident_created_idx on public.verification_decisions (incident_id, created_at desc);

create table public.citizen_feedback (
  id uuid primary key default gen_random_uuid(),
  incident_id uuid not null references public.incidents(id) on delete cascade,
  author_id uuid not null references public.profiles(user_id) on delete restrict,
  rating smallint check (rating between 1 and 5),
  comment text check (char_length(comment) <= 5000),
  created_at timestamptz not null default now(),
  check (rating is not null or comment is not null)
);
create unique index citizen_feedback_one_per_author_incident_idx on public.citizen_feedback (incident_id, author_id);

create table public.safai_coin_accounts (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references public.profiles(user_id) on delete restrict,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner_id)
);

create table public.safai_coin_transactions (
  id uuid primary key default gen_random_uuid(),
  account_id uuid not null references public.safai_coin_accounts(id) on delete restrict,
  incident_id uuid references public.incidents(id) on delete restrict,
  transaction_type public.coin_transaction_type not null,
  status public.coin_transaction_status not null default 'POSTED',
  amount bigint not null check (amount > 0),
  idempotency_key text not null check (char_length(idempotency_key) between 16 and 200),
  created_by uuid references public.profiles(user_id) on delete set null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (idempotency_key)
);
create unique index safai_coin_transactions_one_reward_per_incident_idx
  on public.safai_coin_transactions (incident_id, transaction_type)
  where transaction_type = 'REWARD_CREDIT' and status = 'POSTED';
create index safai_coin_transactions_account_created_idx on public.safai_coin_transactions (account_id, created_at desc);

create table public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  actor_id uuid references public.profiles(user_id) on delete set null,
  actor_role public.app_role,
  action text not null check (char_length(action) between 3 and 200),
  entity_type text not null check (char_length(entity_type) between 3 and 100),
  entity_id uuid,
  request_id uuid,
  before_state jsonb,
  after_state jsonb,
  created_at timestamptz not null default now()
);
create index audit_logs_entity_created_idx on public.audit_logs (entity_type, entity_id, created_at desc);
create index audit_logs_actor_created_idx on public.audit_logs (actor_id, created_at desc);

create table public.notifications (
  id uuid primary key default gen_random_uuid(),
  recipient_id uuid not null references public.profiles(user_id) on delete cascade,
  incident_id uuid references public.incidents(id) on delete set null,
  event_type text not null check (char_length(event_type) between 3 and 100),
  payload jsonb not null default '{}'::jsonb,
  status public.notification_status not null default 'PENDING',
  read_at timestamptz,
  created_at timestamptz not null default now(),
  sent_at timestamptz,
  check ((status = 'READ') = (read_at is not null))
);
create index notifications_recipient_read_created_idx on public.notifications (recipient_id, read_at, created_at desc);

create function public.set_updated_at()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger profiles_set_updated_at before update on public.profiles
for each row execute function public.set_updated_at();
create trigger incidents_set_updated_at before update on public.incidents
for each row execute function public.set_updated_at();
create trigger driver_assignments_set_updated_at before update on public.driver_assignments
for each row execute function public.set_updated_at();
create trigger safai_coin_accounts_set_updated_at before update on public.safai_coin_accounts
for each row execute function public.set_updated_at();

create function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public, auth
as $$
begin
  insert into public.profiles (user_id, display_name)
  values (new.id, nullif(trim(new.raw_user_meta_data ->> 'display_name'), ''));
  insert into public.user_roles (user_id, role)
  values (new.id, 'CITIZEN');
  return new;
end;
$$;

create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();

create function public.prevent_profile_privilege_changes()
returns trigger
language plpgsql
set search_path = public, auth
as $$
begin
  if auth.uid() is not null and auth.uid() = old.user_id then
    if new.user_id <> old.user_id
       or new.account_status <> old.account_status
       or new.created_at <> old.created_at then
      raise exception 'protected profile fields cannot be changed by the user';
    end if;
  end if;
  return new;
end;
$$;
create trigger profiles_prevent_privilege_changes
before update on public.profiles
for each row execute function public.prevent_profile_privilege_changes();

create function public.prevent_notification_mutation()
returns trigger
language plpgsql
set search_path = public, auth
as $$
begin
  if auth.uid() is not null and auth.uid() = old.recipient_id then
    if new.recipient_id <> old.recipient_id
       or new.incident_id is distinct from old.incident_id
       or new.event_type <> old.event_type
       or new.payload <> old.payload
       or new.created_at <> old.created_at
       or new.sent_at is distinct from old.sent_at
       or new.status not in ('PENDING', 'READ') then
      raise exception 'notification fields cannot be changed by recipient';
    end if;
  end if;
  return new;
end;
$$;
create trigger notifications_prevent_mutation
before update on public.notifications
for each row execute function public.prevent_notification_mutation();

create function public.validate_incident_media_reference()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  reporter uuid;
begin
  select reporter_id into reporter from public.incidents where id = new.incident_id;
  if reporter is null then
    raise exception 'incident media must reference an existing incident';
  end if;
  if new.media_kind = 'REPORT' then
    if new.storage_bucket <> 'incident-media' or new.uploaded_by <> reporter then
      raise exception 'report media must be uploaded by the reporting citizen into incident-media';
    end if;
  elsif new.media_kind = 'CLEANUP' then
    if new.storage_bucket <> 'cleanup-evidence' or not exists (
      select 1 from public.driver_assignments da
      where da.incident_id = new.incident_id and da.driver_id = new.uploaded_by
    ) then
      raise exception 'cleanup media must be uploaded by an assigned driver into cleanup-evidence';
    end if;
  end if;
  return new;
end;
$$;
create trigger incident_media_validate_reference
before insert or update on public.incident_media
for each row execute function public.validate_incident_media_reference();

create function public.validate_cleanup_evidence_reference()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  assignment_incident_id uuid;
  assignment_driver_id uuid;
begin
  select incident_id, driver_id into assignment_incident_id, assignment_driver_id
  from public.driver_assignments where id = new.assignment_id;
  if assignment_incident_id is null
     or assignment_incident_id <> new.incident_id
     or assignment_driver_id <> new.submitted_by then
    raise exception 'cleanup evidence must belong to its assignment and assigned driver';
  end if;
  return new;
end;
$$;
create trigger cleanup_evidence_validate_reference
before insert or update on public.cleanup_evidence
for each row execute function public.validate_cleanup_evidence_reference();

create function public.validate_cleanup_evidence_media_reference()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  evidence_incident_id uuid;
  evidence_submitter uuid;
  media_incident_id uuid;
  media_uploader uuid;
  media_type public.media_kind;
begin
  select incident_id, submitted_by into evidence_incident_id, evidence_submitter
  from public.cleanup_evidence where id = new.evidence_id;
  select incident_id, uploaded_by, media_kind into media_incident_id, media_uploader, media_type
  from public.incident_media where id = new.media_id;
  if evidence_incident_id is null
     or media_incident_id <> evidence_incident_id
     or media_uploader <> evidence_submitter
     or media_type <> 'CLEANUP' then
    raise exception 'cleanup evidence media must be cleanup media from the submitting driver for the same incident';
  end if;
  return new;
end;
$$;
create trigger cleanup_evidence_media_validate_reference
before insert or update on public.cleanup_evidence_media
for each row execute function public.validate_cleanup_evidence_media_reference();

create function public.validate_verification_decision()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  reporter uuid;
  cleanup_performer uuid;
  evidence_incident uuid;
begin
  select reporter_id into reporter from public.incidents where id = new.incident_id;
  select incident_id, submitted_by into evidence_incident, cleanup_performer
  from public.cleanup_evidence where id = new.cleanup_evidence_id;
  if evidence_incident is null or evidence_incident <> new.incident_id then
    raise exception 'verification must reference cleanup evidence for the same incident';
  end if;
  if new.status in ('APPROVED', 'DENIED') then
    if new.decided_by = cleanup_performer then
      raise exception 'cleanup performer cannot verify their own cleanup';
    end if;
    if new.actor_kind = 'CITIZEN' and new.decided_by <> reporter then
      raise exception 'citizen verification must be performed by the reporting citizen';
    end if;
    if new.actor_kind = 'ADMIN' and new.decided_by = reporter and reporter = cleanup_performer then
      raise exception 'reporter who performed cleanup cannot verify as an admin';
    end if;
  end if;
  return new;
end;
$$;
create trigger verification_decisions_validate
before insert or update on public.verification_decisions
for each row execute function public.validate_verification_decision();

-- These narrowly scoped helpers read server-controlled role/assignment data for RLS.
create function public.has_app_role(required_roles public.app_role[])
returns boolean
language sql
stable
security definer
set search_path = public, auth
as $$
  select exists (
    select 1 from public.user_roles ur
    where ur.user_id = (select auth.uid())
      and ur.role = any(required_roles)
      and ur.revoked_at is null
  );
$$;

create function public.can_view_incident(target_incident_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public, auth
as $$
  select exists (
    select 1 from public.incidents i
    where i.id = target_incident_id and i.reporter_id = (select auth.uid())
  )
  or public.has_app_role(array['ADMIN', 'VIEWER', 'SUPERADMIN']::public.app_role[])
  or exists (
    select 1 from public.driver_assignments da
    where da.incident_id = target_incident_id
      and da.driver_id = (select auth.uid())
      and da.status in ('ASSIGNED', 'ACCEPTED', 'EN_ROUTE', 'IN_PROGRESS')
  );
$$;

alter table public.profiles enable row level security;
alter table public.user_roles enable row level security;
alter table public.admin_permissions enable row level security;
alter table public.incidents enable row level security;
alter table public.incident_media enable row level security;
alter table public.ai_analysis_results enable row level security;
alter table public.duplicate_assessments enable row level security;
alter table public.driver_assignments enable row level security;
alter table public.cleanup_evidence enable row level security;
alter table public.cleanup_evidence_media enable row level security;
alter table public.verification_decisions enable row level security;
alter table public.citizen_feedback enable row level security;
alter table public.safai_coin_accounts enable row level security;
alter table public.safai_coin_transactions enable row level security;
alter table public.audit_logs enable row level security;
alter table public.notifications enable row level security;

create policy profiles_select_own_or_admin on public.profiles for select to authenticated
using (user_id = (select auth.uid()) or public.has_app_role(array['ADMIN', 'VIEWER', 'SUPERADMIN']::public.app_role[]));
create policy profiles_update_own on public.profiles for update to authenticated
using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));

create policy user_roles_select_own_or_superadmin on public.user_roles for select to authenticated
using (user_id = (select auth.uid()) or public.has_app_role(array['SUPERADMIN']::public.app_role[]));
create policy admin_permissions_select_own_or_superadmin on public.admin_permissions for select to authenticated
using (admin_user_id = (select auth.uid()) or public.has_app_role(array['SUPERADMIN']::public.app_role[]));

create policy incidents_select_authorized on public.incidents for select to authenticated
using (public.can_view_incident(id));
create policy incidents_insert_own_draft on public.incidents for insert to authenticated
with check (reporter_id = (select auth.uid()) and lifecycle_status = 'DRAFT');

create policy incident_media_select_authorized on public.incident_media for select to authenticated
using (public.can_view_incident(incident_id));
create policy ai_analysis_results_select_authorized on public.ai_analysis_results for select to authenticated
using (public.can_view_incident(incident_id));
create policy duplicate_assessments_select_authorized on public.duplicate_assessments for select to authenticated
using (public.can_view_incident(incident_id) or public.can_view_incident(candidate_incident_id));

create policy driver_assignments_select_authorized on public.driver_assignments for select to authenticated
using (driver_id = (select auth.uid()) or public.has_app_role(array['ADMIN', 'VIEWER', 'SUPERADMIN']::public.app_role[]));

create policy cleanup_evidence_select_authorized on public.cleanup_evidence for select to authenticated
using (public.can_view_incident(incident_id));
create policy cleanup_evidence_insert_assigned_driver on public.cleanup_evidence for insert to authenticated
with check (
  submitted_by = (select auth.uid())
  and status = 'SUBMITTED'
  and exists (
    select 1 from public.driver_assignments da
    where da.id = assignment_id and da.incident_id = cleanup_evidence.incident_id
      and da.driver_id = (select auth.uid())
      and da.status in ('ASSIGNED', 'ACCEPTED', 'EN_ROUTE', 'IN_PROGRESS')
  )
);
create policy cleanup_evidence_media_select_authorized on public.cleanup_evidence_media for select to authenticated
using (exists (select 1 from public.cleanup_evidence ce where ce.id = evidence_id and public.can_view_incident(ce.incident_id)));
create policy cleanup_evidence_media_insert_submitter on public.cleanup_evidence_media for insert to authenticated
with check (exists (select 1 from public.cleanup_evidence ce where ce.id = evidence_id and ce.submitted_by = (select auth.uid())));

create policy verification_decisions_select_authorized on public.verification_decisions for select to authenticated
using (
  exists (select 1 from public.incidents i where i.id = incident_id and i.reporter_id = (select auth.uid()))
  or public.has_app_role(array['ADMIN', 'VIEWER', 'SUPERADMIN']::public.app_role[])
);
create policy verification_decisions_insert_eligible_actor on public.verification_decisions for insert to authenticated
with check (
  status in ('APPROVED', 'DENIED')
  and decided_by = (select auth.uid())
  and (
    (
      actor_kind = 'CITIZEN'
      and exists (select 1 from public.incidents i where i.id = incident_id and i.reporter_id = (select auth.uid()))
      and exists (select 1 from public.cleanup_evidence ce where ce.id = cleanup_evidence_id and ce.incident_id = verification_decisions.incident_id and ce.submitted_by <> (select auth.uid()))
    )
    or (
      actor_kind = 'ADMIN'
      and public.has_app_role(array['ADMIN', 'SUPERADMIN']::public.app_role[])
      and exists (select 1 from public.cleanup_evidence ce where ce.id = cleanup_evidence_id and ce.incident_id = verification_decisions.incident_id and ce.submitted_by <> (select auth.uid()))
    )
  )
);

create policy citizen_feedback_select_authorized on public.citizen_feedback for select to authenticated
using (author_id = (select auth.uid()) or public.has_app_role(array['ADMIN', 'VIEWER', 'SUPERADMIN']::public.app_role[]));
create policy citizen_feedback_insert_own_incident on public.citizen_feedback for insert to authenticated
with check (author_id = (select auth.uid()) and exists (select 1 from public.incidents i where i.id = incident_id and i.reporter_id = (select auth.uid())));

create policy coin_accounts_select_own_or_admin on public.safai_coin_accounts for select to authenticated
using (owner_id = (select auth.uid()) or public.has_app_role(array['ADMIN', 'SUPERADMIN']::public.app_role[]));
create policy coin_transactions_select_own_or_admin on public.safai_coin_transactions for select to authenticated
using (exists (select 1 from public.safai_coin_accounts a where a.id = account_id and a.owner_id = (select auth.uid())) or public.has_app_role(array['ADMIN', 'SUPERADMIN']::public.app_role[]));

create policy audit_logs_select_authorized_admin on public.audit_logs for select to authenticated
using (public.has_app_role(array['ADMIN', 'VIEWER', 'SUPERADMIN']::public.app_role[]));

create policy notifications_select_own on public.notifications for select to authenticated
using (recipient_id = (select auth.uid()));
create policy notifications_update_own on public.notifications for update to authenticated
using (recipient_id = (select auth.uid())) with check (recipient_id = (select auth.uid()));

-- Private buckets; browser clients use scoped object names and RLS/signed URLs.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values
  ('incident-media', 'incident-media', false, 52428800, array['image/jpeg', 'image/png']),
  ('cleanup-evidence', 'cleanup-evidence', false, 52428800, array['image/jpeg', 'image/png'])
on conflict (id) do update set public = excluded.public, file_size_limit = excluded.file_size_limit, allowed_mime_types = excluded.allowed_mime_types;

create policy safaios_storage_insert_own_scoped_upload on storage.objects for insert to authenticated
with check (
  bucket_id in ('incident-media', 'cleanup-evidence')
  and (storage.foldername(name))[1] = (select auth.uid())::text
  and owner_id = (select auth.uid())::text
  and (bucket_id = 'incident-media' or public.has_app_role(array['DRIVER']::public.app_role[]))
);
create policy safaios_storage_select_authorized on storage.objects for select to authenticated
using (
  bucket_id in ('incident-media', 'cleanup-evidence')
  and (
    owner_id = (select auth.uid())::text
    or public.has_app_role(array['ADMIN', 'VIEWER', 'SUPERADMIN']::public.app_role[])
    or exists (
      select 1 from public.incident_media im
      where im.storage_bucket = storage.objects.bucket_id
        and im.object_path = storage.objects.name
        and public.can_view_incident(im.incident_id)
    )
  )
);

revoke all on all tables in schema public from anon;
revoke all on all tables in schema public from authenticated;
grant select, update on public.profiles to authenticated;
grant select on public.user_roles, public.admin_permissions to authenticated;
grant select, insert on public.incidents to authenticated;
grant select on public.incident_media, public.ai_analysis_results, public.duplicate_assessments, public.driver_assignments to authenticated;
grant select, insert on public.cleanup_evidence, public.cleanup_evidence_media, public.verification_decisions, public.citizen_feedback to authenticated;
grant select on public.safai_coin_accounts, public.safai_coin_transactions, public.audit_logs to authenticated;
grant select, update on public.notifications to authenticated;

revoke all on function public.set_updated_at() from public;
revoke all on function public.handle_new_user() from public;
revoke all on function public.prevent_profile_privilege_changes() from public;
revoke all on function public.prevent_notification_mutation() from public;
revoke all on function public.validate_incident_media_reference() from public;
revoke all on function public.validate_cleanup_evidence_reference() from public;
revoke all on function public.validate_cleanup_evidence_media_reference() from public;
revoke all on function public.validate_verification_decision() from public;
revoke all on function public.has_app_role(public.app_role[]) from public;
revoke all on function public.can_view_incident(uuid) from public;
grant execute on function public.has_app_role(public.app_role[]) to authenticated;
grant execute on function public.can_view_incident(uuid) to authenticated;

commit;
