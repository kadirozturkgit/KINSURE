# KINSURE Angular frontend

The Angular application provides Turkish login and registration, an authenticated
insurance dashboard, and searchable create/read/update/delete screens for users,
customers, product types, policies, and claims.

## Run locally

1. Start the FastAPI service on `http://localhost:8000`.
2. From the `frontend` directory, run `npm install` once.
3. Run `npm start -- --host 0.0.0.0` and open `http://localhost:4200`.

The Angular development proxy forwards `/api/v1` to `http://localhost:8000`.
Production Nginx forwards requests from its container to the Windows host backend
on port 8000. Update `proxy.conf.json` and `nginx.conf` if it runs elsewhere.

## Build and container

From the project root:

```powershell
docker build -f frontend/Dockerfile -t kinsure-frontend .
docker run --rm -p 8080:8080 kinsure-frontend
```

Open `http://localhost:8080`. The logo is copied from the root `images` folder
during the frontend build.
