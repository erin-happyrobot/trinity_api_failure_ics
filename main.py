from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import requests
from fastapi import Request
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


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
    environment = os.getenv("ENVIRONMENT")
    if environment == "STAGE":
        url = os.getenv("URL_STAGE")
    else:
        url = os.getenv("URL")

    # Accept JSON body first; fall back to query params for compatibility
    try:
        payload = await request.json()
    except Exception:
        payload = dict(request.query_params)

    API_TOKEN = os.getenv("API_TOKEN")
    # Strip accidental surrounding quotes from .env values
    if API_TOKEN and ((API_TOKEN.startswith('"') and API_TOKEN.endswith('"')) or (API_TOKEN.startswith("'") and API_TOKEN.endswith("'"))):
        API_TOKEN = API_TOKEN[1:-1]
    AUTH_HEADER_NAME = os.getenv("AUTH_HEADER_NAME", "API-Token")
    AUTH_SCHEME = os.getenv("AUTH_SCHEME")  # e.g., "Bearer" or "Token"
    API_TOKEN_QUERY_PARAM = os.getenv("API_TOKEN_QUERY_PARAM")
    ACCEPT = os.getenv("ACCEPT", "application/json")
    EXTRA_HEADER_NAME = os.getenv("EXTRA_HEADER_NAME")
    EXTRA_HEADER_VALUE = os.getenv("EXTRA_HEADER_VALUE")
    API_TOKEN_BODY_FIELD = os.getenv("API_TOKEN_BODY_FIELD")
    USE_FORM = os.getenv("USE_FORM", "0") in ("1", "true", "True")

    headers = {"Accept": ACCEPT}
    if API_TOKEN:
        if AUTH_SCHEME:
            headers["Authorization"] = f"{AUTH_SCHEME} {API_TOKEN}"
        else:
            headers[AUTH_HEADER_NAME] = API_TOKEN
    if EXTRA_HEADER_NAME and EXTRA_HEADER_VALUE:
        headers[EXTRA_HEADER_NAME] = EXTRA_HEADER_VALUE

    if API_TOKEN and API_TOKEN_QUERY_PARAM:
        # Append token to query string if required by upstream
        parsed = urlparse(url)
        query = dict(parse_qsl(parsed.query))
        query[API_TOKEN_QUERY_PARAM] = API_TOKEN
        url = urlunparse(parsed._replace(query=urlencode(query)))


    # Optionally inject token into body
    if API_TOKEN and API_TOKEN_BODY_FIELD:
        if isinstance(payload, dict):
            payload[API_TOKEN_BODY_FIELD] = API_TOKEN

    try:
        if USE_FORM:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            response = requests.post(url, data=payload, headers=headers, timeout=30)
        else:
            headers["Content-Type"] = "application/json"
            response = requests.post(url, json=payload, headers=headers, timeout=30)
        try:
            response_body = response.json()
        except Exception:
            response_body = response.text
        # Avoid leaking secrets: only echo which auth method was used
        auth_hint = (
            (f"Authorization {AUTH_SCHEME}" if AUTH_SCHEME else f"Header {AUTH_HEADER_NAME}")
            if API_TOKEN
            else None
        )
        # Sanitize headers we sent for debugging
        redacted_headers = {}
        for k, v in headers.items():
            if k.lower() == "authorization":
                redacted_headers[k] = v.split(" ")[0] if isinstance(v, str) and " " in v else "set"
            elif any(s in k.lower() for s in ["key", "token", "secret", "auth"]):
                redacted_headers[k] = "<redacted>"
            else:
                redacted_headers[k] = v
        www_auth = response.headers.get("www-authenticate") or response.headers.get("WWW-Authenticate")
        return {
            "status": response.status_code,
            "ok": response.ok,
            "body": response_body,
            "usedAuth": auth_hint,
            "wwwAuthenticate": www_auth,
            "requestUrl": url,
            "requestHeaders": redacted_headers,
            "usedForm": USE_FORM,
        }
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


