# TodoMate + Budget (Django + DRF)

Backend-first web app that combines a schedule/todo manager and a personal budget ledger.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata seed/seed.json  # optional
python manage.py runserver
```

Open: http://127.0.0.1:8000

- Admin: /admin
- API root: /api/
- Tasks UI: /tasks/
- Finance UI: /finance/

## Tech
- Django 5, Django REST Framework, SimpleJWT, django-filter, CORS headers
- SQLite by default. Postgres via Docker compose.
