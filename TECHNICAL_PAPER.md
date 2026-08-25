# Internship and OJT Management System

## Abstract

This project is a Django-based web application for managing student internship and on-the-job training (OJT) workflows. It centralizes internship postings, applications, placements, daily time records, document submission and validation, supervisor evaluations, role-specific dashboards, Excel reporting, and an audit trail of authenticated activity. The system is built as a set of modular Django apps (`accounts`, `internships`, `applications`, `timelog`, `documents`, `evaluations`, `dashboard`, `auditlog`) sharing a single custom user model with three roles: student, coordinator, and company supervisor.

## Problem Statement

OJT coordination at most schools is handled through spreadsheets, printed forms, and email — a process that makes it difficult to track which students still need placements, whether required hours are being logged consistently, whether required documents (MOA, waiver, resume, weekly reports) have actually been submitted and validated, and whether supervisor evaluations were completed and graded fairly. Because these records live in separate places, cross-checking a single student's status (application → placement → hours → documents → evaluation) is slow and error-prone, and there is no single audit trail of who changed what. This system replaces that scattered process with one shared, role-aware workflow.

## Objectives

- Provide self-service, role-based registration and access for students and company supervisors, with coordinator accounts provisioned separately.
- Let coordinators create, edit, and close internship postings, and let students discover and apply to them.
- Automate the transition from an approved application to a placement with an assigned company supervisor.
- Record daily attendance and accomplishments, and track progress toward each student's required hours.
- Collect and validate required documents per student.
- Collect structured supervisor evaluations and convert them into a comparable score and letter grade.
- Give each role a dashboard suited to what they need to see, and give coordinators an exportable report.
- Maintain a tamper-evident record of authenticated activity for accountability.

## System Architecture

The system is a standard Django 6.0 project (`ojt_management_system`) with eight installed apps, each responsible for one part of the workflow:

| App | Responsibility |
|---|---|
| `accounts` | `CustomUser` (extends `AbstractUser` with a `role` field), `StudentProfile`, `CompanyProfile`, registration, login/logout, role-based access decorators |
| `internships` | `CompanyPosting` (a company record selectable when creating a posting) and `InternshipPosting` (title, location, required hours, slots, deadline); CRUD views restricted to coordinators; Excel export via `openpyxl` |
| `applications` | `ApplicationRecord` (student → posting, with status pending/approved/rejected) and `PlacementRecord` (created once an application is approved, with an assigned company supervisor) |
| `timelog` | `DailyTimeLog` — one row per student per date, with time in/out, accomplishment text, and `hours_completed`; class methods aggregate total hours and remaining hours against a required-hours constant |
| `documents` | `SubmittedDocument` — typed uploads (MOA, waiver, resume, weekly report) with a pending/validated/rejected status a coordinator sets |
| `evaluations` | `EvaluationRecord` — a supervisor's 1–5 ratings across four criteria (overall rating, punctuality, professionalism, teamwork) for a given student, with `average_score`, `score_percent`, and `grade` (A–F) computed as model properties |
| `dashboard` | Role-specific dashboard views and charts (built on the aggregated data from the apps above) |
| `auditlog` | `AuditLog` model plus a request-level middleware that records the method, path, status code, and client IP of every authenticated request |

Templates use Django's template language with Bootstrap for layout and Chart.js for dashboard charts, sharing a single theme stylesheet. Data access is entirely through the Django ORM — there is no separate API layer. SQLite is the default local-development database; PostgreSQL is used in the Docker Compose deployment configuration, selected via the `DATABASE_ENGINE` environment variable. Static files (CSS/JS) are collected at build time with `collectstatic` and served in production by WhiteNoise middleware directly from the gunicorn process, so no separate static-file server is required.

**Cross-app relationships.** `ApplicationRecord` and `PlacementRecord` (in `applications`) both hold a foreign key to `InternshipPosting` (in `internships`), so a posting's applications and placements are visible from either side. `DailyTimeLog`, `SubmittedDocument`, and `EvaluationRecord` each key off the student's user account directly rather than the placement, which keeps those apps decoupled from `applications` at the cost of not scoping a time log or document to a specific placement when a student has more than one.

**Company registration and postings.** A company supervisor who self-registers gets a `CompanyProfile`. On save, the registration form also creates (or updates, on later profile edits) a linked `CompanyPosting` record via a `linked_profile` one-to-one field, so the company appears automatically in the dropdown a coordinator uses when creating an internship posting — without the coordinator having to re-type the company name. Coordinators can still add a `CompanyPosting` manually for partner companies that don't have a system account.

## Security and Integrity

- **Authentication and authorization.** `CustomUser` extends Django's `AbstractUser` with a `role` field. Two decorators, `role_required` and `role_login_required` (which composes `login_required` with `role_required`), gate views by role and redirect anonymous users to the login page instead of exposing a raw 403.
- **CSRF protection.** All state-changing forms (registration, postings, applications, time logs, document uploads, evaluations) use Django's built-in CSRF token and middleware.
- **Data integrity constraints.** `ApplicationRecord` and `PlacementRecord` enforce a unique `(student, internship)` pair at the database level, so a student cannot double-apply to or hold two placements for the same posting. `DailyTimeLog` enforces a unique `(student, entry_date)` pair. `EvaluationRecord` enforces a unique `(student, supervisor)` pair and validates in `clean()` that a supervisor cannot evaluate themselves and that every rating falls within 1–5.
- **Deletion guards.** A posting cannot be deleted from `internships.internship_delete` while it still has applications or placements attached; the view rejects the deletion with a message rather than cascading.
- **Audit trail.** `AuditLogMiddleware` records every authenticated, non-static request (method, path, status code, client IP, resolved via `X-Forwarded-For` when present) to the `AuditLog` model, exposed to coordinators via `/activity-log/`.
- **Production hardening.** `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, HSTS (`SECURE_HSTS_SECONDS=31536000` with subdomains and preload), `SECURE_CONTENT_TYPE_NOSNIFF`, and a same-origin referrer policy are all controlled by a dedicated `BEHIND_HTTPS_PROXY` environment variable rather than by `DEBUG`. This is deliberate: tying them to `DEBUG=False` would force an HTTPS redirect and secure-only cookies even when the app is served over plain HTTP (e.g. local Docker testing on `http://localhost:8000`), which causes a redirect loop and silently blocks login. `BEHIND_HTTPS_PROXY` should only be set to `True` once the app actually sits behind a reverse proxy or platform that terminates real HTTPS and forwards `X-Forwarded-Proto`. `SECRET_KEY` must be supplied via environment variable when `DEBUG=False`; there is no insecure fallback in that mode.

## Testing and Deployment

Automated tests exist for `accounts`, `internships`, `evaluations`, and `auditlog` (8 tests total as of this writing, covering registration/role behavior, posting/company linkage, evaluation grading and self-evaluation prevention, and audit-log creation); `applications`, `timelog`, `documents`, and `dashboard` do not yet have dedicated test modules. Before release, the project should be validated with:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

A `Dockerfile` and `docker-compose.yml` are included for a PostgreSQL-backed deployment, and `DEPLOYMENT.md` documents the full checklist (environment configuration, `createsuperuser`, TLS termination at a reverse proxy, `manage.py check --deploy`). The Docker Compose configuration has been built and run end-to-end locally: the `db` service includes a `pg_isready` healthcheck so `web` waits for Postgres to actually accept connections before running migrations, and a named volume persists uploaded media across container restarts. A `backup_project --include-media` management command is provided for backups. The project is tracked in a GitHub repository. As of this writing, a public deployment (Render) is planned but not yet completed.

## Limitations and Future Work

- No external hosting account or production domain is included in the repository; a live deployment must be completed separately using the provided Docker configuration.
- Test coverage is uneven across apps — `applications`, `timelog`, `documents`, and `dashboard` would benefit from dedicated test modules covering the application → placement transition, hours aggregation, and document validation flows.
- `DailyTimeLog`, `SubmittedDocument`, and `EvaluationRecord` are keyed to the student's user account rather than to a specific `PlacementRecord`, which is sufficient while a student holds at most one active placement but would need to change if the system is extended to support multiple concurrent placements per student.
- Company self-registration links one `CompanyProfile` to one `CompanyPosting`; supporting a company with multiple supervisor accounts under one posting profile is a possible future enhancement.
- Reporting is currently limited to a single Excel export of internship postings; richer reporting (e.g., per-student hour summaries, evaluation-grade distributions) could be added to the coordinator dashboard.
