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
def health(request: Request):
    url = os.getenv("URL")
    params = {
        "shipmentId": request.query_params.get("shipmentId"),
        "mcNumber": request.query_params.get("mcNumber"),
        "dotNumber": request.query_params.get("dotNumber"),
        "contactName": request.query_params.get("contactName"),
        "contactPhoneNumber": request.query_params.get("contactPhoneNumber"),
        "currentCity": request.query_params.get("currentCity"),
        "currentState": request.query_params.get("currentState"),
        "note": request.query_params.get("note"),
        "offeredRate": request.query_params.get("offeredRate"),
        "callRate": request.query_params.get("callRate")
    }
    try:
        response = requests.post(url, json=params, headers={"Content-Type": "application/json"})
        print(response.status_code)
        return {"status": response.status_code}
    except Exception as e:
        print(e)
        return {"status": response.status_code}


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


