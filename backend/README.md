# KINSURE FastAPI backend

Backend source is in `app/`. The service uses Oracle's `oracledb` Thin mode and
expects the tables in `sql/schema.sql` to be installed in the target schema.

1. Copy the project-root `.env.example` to `.env` and set Oracle credentials,
   DSN, and a private `JWT_SECRET_KEY`.
2. Apply `backend/sql/schema.sql` once to the Oracle schema.
3. Install project-root `requirements.txt` and run
   `uvicorn app.main:app --app-dir backend --reload`.
4. Open `/docs` for the Turkish CRUD and authentication endpoints.

All data-changing API endpoints require a bearer token. New customer, policy,
and claim records receive `CREATED_BY` from the authenticated token rather than
from client input. Passwords are stored as Argon2 hashes and are never returned
by the API.
