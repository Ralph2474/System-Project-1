# WebSys-Compliance — Internship & OJT Management System

A Django web application for running a school's internship / on-the-job training (OJT) programme end to end:
internship postings, applications, placements, daily time records, document submission and validation,
supervisor evaluations, role-specific dashboards, Excel reporting and an audit trail.

## Roles

| Role | What they do | Account |
|---|---|---|
| **Student** | Browse and apply for internships, log daily time, upload required documents, view evaluations | Self-registers at `/register/` |
| **Coordinator** | Manage companies and postings, approve/reject applications, assign supervisors, validate documents, view the activity log | Created by an administrator (admin panel, **Role = Coordinator**) |
| **Company Supervisor** | Monitor assigned interns' hours and submit performance evaluations | Self-registers at `/register/` |

The **administrator** (created with `createsuperuser`) is not a fourth role: it is used for the Django admin panel at
`/admin/` to manage accounts and data.

## Features

- **Role-based accounts** — registration with role-specific required fields (student number and course, or company name and contact person); each role gets its own menu, dashboard and permissions.
- **Internship postings** — coordinators create, edit, close and delete postings (company, location, required hours, slots, deadline); students see only open postings and can search, filter and sort them.
- **Applications & placements** — students apply once per posting and can withdraw pending applications; approving an application uses one slot and creates a placement, to which the coordinator assigns a company supervisor. A student can hold only one placement.
- **Daily time record (DTR)** — time in/out and accomplishments with hours calculated automatically (overnight shifts supported) and progress tracked against the posting's required hours. No future dates, no duplicates, nothing before the placement start date.
- **Documents** — students upload MOA, waiver, résumé and weekly reports (PDF/DOC/DOCX, max 10 MB); coordinators validate or reject them with notes. Files are private: they are served only to the owning student and coordinators.
- **Evaluations** — supervisors rate assigned students 1–5 on four criteria; the system computes the average, percentage and letter grade (A–F), visible to the student under **Evaluations**.
- **Dashboards & reporting** — role-specific dashboards with Chart.js charts, and an Excel (.xlsx) export of postings for coordinators.
- **Audit log** — every signed-in request (user, action, page, status, IP) is recorded and viewable by coordinators under **Activity Log**.
- **Responsive UI** — Bootstrap 5 with a custom theme; works on desktop, tablet and phone.

## Tech stack

Python 3.13 · Django 6.0 · PostgreSQL 16 (SQLite for local development) · gunicorn + WhiteNoise ·
Bootstrap 5 + Chart.js · openpyxl (Excel export) · Docker Compose. See `requirements.txt` for exact versions.

## Project layout

| App | Responsibility |
|---|---|
| `accounts` | Custom user model with roles, registration, login, password reset, student/company profiles, role decorators |
| `internships` | Partner companies, internship postings, Excel export |
| `applications` | Applications, coordinator decisions, placements and supervisor assignment |
| `timelog` | Daily time records and hours progress |
| `documents` | Document upload, validation and protected file download |
| `evaluations` | Supervisor evaluations and grading |
| `dashboard` | Role-specific dashboards and charts |
| `auditlog` | Audit middleware, activity log page, `backup_project` command |

Shared templates are in `templates/` and the theme stylesheet is `static/css/theme.css`.

## Quick start with Docker (recommended)

```powershell
Copy-Item docker-compose.example.yml docker-compose.yml
Copy-Item .env.example .env          # then edit .env: SECRET_KEY, POSTGRES_PASSWORD, TIME_ZONE
docker compose up --build -d
docker compose exec web python manage.py createsuperuser
```

Open <http://localhost:8000> (admin panel: <http://localhost:8000/admin/>). Full instructions, backups/restore,
the production checklist and troubleshooting are in **`DEPLOYMENT.md`**.

## Local development (without Docker)

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

With no environment variables the app runs with `DEBUG=True` and SQLite (`db.sqlite3`).
Go to <http://127.0.0.1:8000/register/> to create student or supervisor accounts. To get a coordinator,
sign in at `/admin/`, open **Users** and set a user's **Role** to **Coordinator** (a new superuser's role is Student by default).

## Configuration

Environment variables (template: `.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `DEBUG` | `True` | Must be `False` in any shared or public deployment |
| `SECRET_KEY` | — | Required when `DEBUG=False` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated host names the site answers to |
| `TIME_ZONE` | `UTC` | School's local time zone (e.g. `Asia/Singapore`); date rules use the local date |
| `DATABASE_ENGINE` | `sqlite` | `sqlite` or `postgresql` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | — | Used when `DATABASE_ENGINE=postgresql` |
| `BEHIND_HTTPS_PROXY` | `False` | `True` only behind an HTTPS-terminating proxy (enables HTTPS redirect, secure cookies, HSTS) |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL` | empty | SMTP for password-reset emails (console output when `DEBUG=True`) |

`docker-compose.yml` and `.env` contain secrets and are git-ignored; commit only the `.example` templates.

## Backups

```powershell
docker compose exec web python manage.py backup_project --include-media   # Docker
python manage.py backup_project --include-media                           # local
```

Each backup is a timestamped folder in `backups/` with `data.json` and the uploaded `media/`.
Restore steps are in `DEPLOYMENT.md`.

## Testing

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

All three pass on the current version (8 unit tests). In addition, a 99-check end-to-end scenario test
covering every workflow, validation rule and permission was run with `DEBUG` on and off; its results are
reported in the technical paper.

## Documentation

| Document | Contents |
|---|---|
| `OJT_User_Manual.pdf` | Illustrated step-by-step guide for each role, administrator tasks and troubleshooting |
| `OJT_Technical_Paper.pdf` | Objectives, architecture, data model, business rules, security, testing results and limitations |
| `OJT_Deployment_Guide.pdf` / `DEPLOYMENT.md` | Installation, configuration, operations, backup/restore, production checklist, Render |
| `OJT_Roles_and_Features.pdf` | Short overview of the three roles and what each can do |
| `USER_MANUAL.md`, `TECHNICAL_PAPER.md` | Earlier plain-text versions of the manual and paper |

## Known limitations

- A student can hold one placement at a time; time logs, documents and evaluations are linked to the student rather than to a specific placement.
- Password-reset emails are delivered only after SMTP (`EMAIL_*`) is configured.
- Automated unit tests cover `accounts`, `internships`, `evaluations` and `auditlog`; `applications`, `timelog`, `documents` and `dashboard` are not yet covered by test modules in the repository.
- Reporting is limited to the dashboards and the Excel export of postings.
- The application has not yet been deployed to a public host; that requires a hosting provider, domain and TLS certificate (see `DEPLOYMENT.md`).
