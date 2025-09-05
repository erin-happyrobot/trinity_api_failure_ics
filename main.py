from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import requests
from fastapi import Request


app = FastAPI(title="Trinity API", version="0.1.0")

# Configure CORS. Optionally set CORS_ORIGINS to a comma-separated list in env.
_cors_env = os.environ.get("CORS_ORIGINS", "*")
allow_origins = ["*"] if _cors_env.strip() == "*" else [o.strip() for o in _cors_env.split(",") if o.strip()]

# Load environment variables from .env if present
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Trinity FastAPI is running."}


@app.get("/health")
def health_get():
    return {"status": "ok"}


@app.post("/health")
async def health_post(request: Request):
    url = os.getenv("URL")
    if not url:
        return {"status": 500, "ok": False, "error": "URL is not configured"}

    # Accept JSON body first; fall back to query params for compatibility
    try:
        payload = await request.json()
    except Exception:
        payload = dict(request.query_params)

    headers = {"Content-Type": "application/json"}

    # Optional authorization mechanisms via environment variables
    # - AUTH_BEARER -> sets Authorization: Bearer <token>
    # - API_KEY (+ optional API_KEY_HEADER_NAME, default X-API-KEY)
    # - BASIC_USER/BASIC_PASS for HTTP Basic auth
    bearer_token = os.getenv("AUTH_BEARER")
    api_key = os.getenv("API_KEY")
    api_key_header_name = os.getenv("API_KEY_HEADER_NAME", "X-API-KEY")
    basic_user = os.getenv("BASIC_USER")
    basic_pass = os.getenv("BASIC_PASS")

    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    if api_key:
        headers[api_key_header_name] = api_key

    auth = None
    if basic_user and basic_pass:
        auth = (basic_user, basic_pass)

    try:
        response = requests.post(url, json=payload, headers=headers, auth=auth, timeout=30)
        try:
            response_body = response.json()
        except Exception:
            response_body = response.text
        return {"status": response.status_code, "ok": response.ok, "body": response_body}
    except Exception as e:
        return {"status": 500, "ok": False, "error": str(e)}


@app.get("/env")
def env_info():
    return {
        "port": os.environ.get("PORT"),
        "environment": os.environ.get("RAILWAY_ENVIRONMENT_NAME"),
    }


if __name__ == "__main__":
    # Allow running via: python main.py
    try:
        import uvicorn  # type: ignore
    except Exception as exc:
        raise SystemExit(
            "Uvicorn is not installed. Run 'pip install -r requirements.txt' first."
        ) from exc

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


