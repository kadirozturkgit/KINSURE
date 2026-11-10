# KINSURE FastAPI backend

Backend source is in `app/`. The service uses Oracle's `oracledb` Thin mode and
expects the tables in `sql/schema.sql` to be installed in the target schema.

1. Copy the project-root `.env.example` to `backend/.env` and set Oracle
   credentials, the DSN `127.0.0.1:1522/FREEPDB1`, and a private
   `JWT_SECRET_KEY`.
2. From the project root, start the supported Oracle Free database with
   `docker compose --env-file backend/.env up -d oracle`.
3. Apply `backend/sql/schema.sql` once to the Oracle schema if it has not already
   been imported.
4. Install project-root `requirements.txt` and run
   `uvicorn app.main:app --app-dir backend --reload`.
5. Open `/docs` for the Turkish CRUD and authentication endpoints.

All data-changing API endpoints require a bearer token. New customer, policy,
and claim records receive `CREATED_BY` from the authenticated token rather than
from client input. Passwords are stored as Argon2 hashes and are never returned
by the API.
