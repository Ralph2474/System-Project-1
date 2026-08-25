# User Manual

## Accessing the system

1. Open the application URL.
2. Select **Create account** and choose Student or Company Supervisor.
3. Complete the role-specific profile fields.
4. Sign in to open the role dashboard.

## Student workflow

1. Browse open internship postings.
2. Open a posting and submit an application with a cover letter.
3. Track application status from **My Applications**.
4. After placement approval, open **Time Log** to record time in, time out, and accomplishments.
5. Upload required files from **Documents** and monitor validation status.
6. Review submitted evaluations from **Evaluations**.
7. Update academic details from **Profile**.

## Coordinator workflow

1. Create and manage internship postings.
2. Review and decide student applications.
3. Maintain placement details.
4. Validate or reject submitted documents.
5. Export internship postings from **Export Excel**.
6. Review system activity from **Activity Log**.

## Company supervisor workflow

1. Update company contact details from **Company Profile**.
2. Review assigned students.
3. Submit evaluation ratings and comments.
4. View calculated percentage scores and letter grades.

## Backups

If running via Docker Compose:

```powershell
docker compose exec web python manage.py backup_project --include-media
```

If running locally with a virtual environment instead:

```powershell
.\.venv\Scripts\python.exe manage.py backup_project --include-media
```

Store generated backups outside the application machine and test restoration regularly.

## Common recovery steps

- If a form shows an error, correct the highlighted fields and submit again.
- If a posting is closed or full, return to the internship list and choose another open posting.
- If a document is validated, upload a corrected replacement rather than deleting the validated record.
- For permission errors, sign in with the role that owns the requested workflow.
