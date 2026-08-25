# Deployment

## Docker Compose

1. Copy `.env.example` to a secure environment configuration and replace every placeholder secret.
2. Update the PostgreSQL password in `docker-compose.yml` or move it to a secret manager. **The `POSTGRES_PASSWORD` set under the `db` service and the one set under the `web` service must be identical** — `web` uses its copy to authenticate against the database `db` was initialized with, and a mismatch fails with `password authentication failed`.
3. If you change the Postgres password (or are starting fresh), reset the database volume so it re-initializes with the new credentials, then build and start the services:

```powershell
docker compose down -v
docker compose up --build
```

If you're just restarting without changing the password, drop `-v` so existing data is kept:

```powershell
docker compose up --build
```

4. Create an administrator in a separate shell, once both containers report as running (`docker compose ps` should show `db` as `healthy` and `web` as `Up`):

```powershell
docker compose exec web python manage.py createsuperuser
```

5. Open `http://localhost:8000` or place the web service behind an HTTPS reverse proxy.

Note: `docker-compose.yml` is excluded from version control via `.gitignore` once it contains a real password, so it will not appear in the GitHub repository.

## Production requirements

- Set `DEBUG=False`.
- Set a long random `SECRET_KEY`.
- Set `ALLOWED_HOSTS` to the real domain names.
- Terminate TLS at the reverse proxy, forward `X-Forwarded-Proto: https`, and set `BEHIND_HTTPS_PROXY=True` so Django enforces HTTPS and secure cookies. Leave it `False` for local/plain-HTTP testing (e.g. `docker compose up` on your own machine) - turning it on without real HTTPS in front will redirect-loop and block logins.
- Schedule `manage.py backup_project --include-media` and copy backups to separate storage.
- Run `manage.py check --deploy` before release.

The repository contains deployment artifacts, but an actual public deployment requires a hosting provider, domain, TLS certificate, and production credentials supplied by the project owner.

## Public deployment (Render) — planned

1. Push the repository to GitHub (already done; `docker-compose.yml` stays untracked).
2. Create a free PostgreSQL instance on Render and note its connection details.
3. Create a Web Service on Render pointing at this repository's `Dockerfile`.
4. Set environment variables on the Render service: `DEBUG=False`, a real random `SECRET_KEY`, `DATABASE_ENGINE=postgresql`, the `POSTGRES_*` values from step 2, `ALLOWED_HOSTS=<service-name>.onrender.com`, and `BEHIND_HTTPS_PROXY=True` (safe here, since Render terminates HTTPS in front of the service).
5. Override the service's start command to run migrations before serving:
   `sh -c "python manage.py migrate && gunicorn ojt_management_system.wsgi:application --bind 0.0.0.0:$PORT"`
6. Create the superuser via Render's Shell tab: `python manage.py createsuperuser`.

Known limitation on Render's free tier: the web service filesystem is ephemeral, so uploaded documents (`media/`) do not persist across redeploys or restarts; a persistent disk (paid) would be required for that in a real production deployment. The free Postgres instance also expires 30 days after creation unless upgraded.
