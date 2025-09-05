from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os


app = FastAPI(title="Trinity API", version="0.1.0")

# Configure CORS. Optionally set CORS_ORIGINS to a comma-separated list in env.
_cors_env = os.environ.get("CORS_ORIGINS", "*")
allow_origins = ["*"] if _cors_env.strip() == "*" else [o.strip() for o in _cors_env.split(",") if o.strip()]

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
def health():
    return {"status": "ok"}


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


