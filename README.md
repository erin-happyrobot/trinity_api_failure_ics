Trinity FastAPI Service

A minimal FastAPI app configured for deployment on Railway.

Endpoints

- GET /: Basic welcome response
- GET /health: Health check endpoint
- GET /env: Returns a small subset of environment info (for debugging)

Local Development

1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the server in development with auto-reload:

```
uvicorn main:app --reload
```

The server will be available at http://127.0.0.1:8000.

CORS

By default, CORS is set to allow all origins. To restrict, set CORS_ORIGINS to a comma-separated list of origins, e.g.:

```
export CORS_ORIGINS="https://your.site,https://another.site"
```

Deploying to Railway

1. Push this project to a Git repository (e.g., GitHub).
2. Create a new project on Railway and connect your repository.
3. Railway will detect Python and install requirements.txt using Nixpacks.
4. Start command is defined in Procfile:

```
web: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

5. Deploy. Railway will provide the PORT environment variable automatically.

Notes

- If you need environment variables, add them in Railway Project Settings.
- For production, you can adjust workers via Uvicorn flags (e.g., --workers 2).

