# WebSys-Compliance — Internship & OJT Management System

A Django web application for managing student internship / on-the-job training (OJT) workflows end to end: postings, applications, placements, daily time records, document submission, supervisor evaluations, dashboards, and audit history.

## Features

- **Role-based accounts** — self-service registration at `/register/` for students and company supervisors, with role-specific required fields (student number/course, or company name/contact person). Coordinator accounts are created separately (not self-registered).
- **Internship postings** — coordinators create, edit, and delete postings (company, location, required hours, slots, deadline); students browse and filter open postings.
- **Applications & placements** — students apply, coordinators approve/reject, and an approved application automatically creates a placement with supervisor assignment.
- **Daily time record (DTR)** — time in/out and accomplishment text, with hours auto-calculated and tracked against each placement's required hours.
- **Documents** — students upload required files; coordinators validate or reject them.
- **Evaluations** — company supervisors submit 1–5 ratings that are averaged into a percentage score and letter grade (A–F), shown in the student's dashboard.
- **Dashboards & reporting** — role-specific dashboards with charts, plus an Excel export of internship postings for coordinators.
- **Audit log** — authenticated, state-changing requests are recorded and viewable from **Activity Log**.

## Tech stack

Django 6.0 (see `requirements.txt`), Django templates + Bootstrap + Chart.js for the frontend, SQLite for local development, PostgreSQL for deployment (via `DATABASE_ENGINE=postgresql` and the `POSTGRES_*` environment variables). `openpyxl` powers the Excel export and `psycopg` is the PostgreSQL driver.

## Project layout

The project is split into focused Django apps, each installed in `ojt_management_system/settings.py`:

| App | Responsibility |
|---|---|
| `accounts` | Custom user model, roles, registration, student/company profiles |
| `internships` | Internship postings and the company records they belong to |
| `applications` | Student applications and placement creation |
| `timelog` | Daily time records / accomplishment log |
| `documents` | Document submission and validation |
| `evaluations` | Supervisor evaluation forms and grading |
| `dashboard` | Role-specific dashboards and charts |
| `auditlog` | Request auditing and the activity log view |

## Getting started (local development)

```bash
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

By default the app runs with `DEBUG=True` and a SQLite database at `db.sqlite3` — no environment variables are required for local development. Visit `http://127.0.0.1:8000/register/` to create a student or company supervisor account, or sign in at `/admin/` with the superuser account to act as a coordinator.

## Configuration

Environment variables (see `.env.example`):

| Variable | Purpose |
|---|---|
| `DEBUG` | `True`/`False`. Defaults to `True`. |
| `SECRET_KEY` | Required when `DEBUG=False`. |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames. |
| `DATABASE_ENGINE` | `sqlite` (default) or `postgresql`. |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | Used when `DATABASE_ENGINE=postgresql`. |

## Deployment

A `Dockerfile` and `docker-compose.yml` are included for a PostgreSQL-backed deployment. See `DEPLOYMENT.md` for the full checklist. **Note:** these are deployment artifacts only — the application has not yet been deployed to a public host; that step still requires a hosting provider, domain, and TLS certificate.

## Backups

```bash
python manage.py backup_project --include-media
```

## Testing

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Documentation

- `USER_MANUAL.md` — per-role walkthroughs and recovery steps.
- `DEPLOYMENT.md` — deployment checklist and production requirements.
- `TECHNICAL_PAPER.md` — architecture, security, and testing overview.

## Known limitations

- Company self-registration now creates a linked internship-postings record automatically, but a coordinator can still add a manual company entry for partners without a system account.
- Automated test coverage exists (`accounts`, `internships`, `evaluations`, `auditlog`) but is not comprehensive across every app.
- The application has not been deployed to a public host.
