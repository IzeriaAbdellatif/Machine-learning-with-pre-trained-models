# Alembic migrations

This folder contains Alembic configuration to manage database migrations for the Backend.

Quick usage (from the `Backend` folder):

- Create a new autogenerate migration:

```bash
# Activate your venv first
source venv/bin/activate
alembic revision --autogenerate -m "initial"
```

- Apply migrations:

```bash
alembic upgrade head
```

Notes:
- The Alembic `env.py` uses `app.core.config.settings.DATABASE_URL`.
- The metadata used for autogenerate is `app.db.session.Base.metadata`.
- If your database isn't running, `alembic revision --autogenerate` may fail; you can still create an empty migration with `alembic revision -m "msg"` and edit it manually.
