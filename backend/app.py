import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib

app = FastAPI(
    title="WhatsApp Malicious Message Detector",
    description="Backend API to classify messages and detect manipulative or honeytrap patterns.",
    version="1.0.0",
)

# CORS configuration (allows override via ALLOWED_ORIGINS env variable)
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "honeytrap_detector.joblib"),
)


class PredictRequest(BaseModel):
    text: str


class PredictResponse(BaseModel):
    label: str
    score: Optional[float] = None
    tags: List[str] = []


def load_model(path: str = MODEL_PATH):
    """Load the ML model from disk if available."""
    if not os.path.exists(path):
        return None, f"Model file '{path}' does not exist"
    try:
        loaded = joblib.load(path)
        return loaded, None
    except Exception as e:
        return None, str(e)


model, load_error = load_model(MODEL_PATH)


def extract_tags(text: str) -> List[str]:
    """Detect contextual threat tags from message keywords."""
    tags: List[str] = []
    lowered = text.lower()

    if any(w in lowered for w in ["urgent", "asap", "hurry", "now", "immediately", "action required"]):
        tags.append("urgency")
    if any(w in lowered for w in ["baby", "dear", "love", "flirt", "kiss", "honey", "sweetheart"]):
        tags.append("flirty")
    if any(w in lowered for w in ["trust", "secret", "don’t tell", "don't tell", "dont tell", "only you", "believe me"]):
        tags.append("manipulation")

    return tags


@app.get("/")
def root():
    if model is not None:
        return {
            "status": "model loaded",
            "mode": "ml_model",
            "model_path": MODEL_PATH,
        }
    return {
        "status": "ready (heuristic fallback)",
        "mode": "heuristic",
        "message": (
            "No trained model file found. Running in rule-based heuristic mode. "
            "Place 'honeytrap_detector.joblib' in the backend directory to enable ML inference."
        ),
    }


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text provided")

    tags = extract_tags(text)

    # Path 1: ML Model inference if available
    if model is not None:
        try:
            pred = model.predict([text])
            label_raw = pred[0]

            # Normalize label
            if isinstance(label_raw, (int, float)):
                label = "malicious" if int(label_raw) == 1 else "normal"
            else:
                label = "malicious" if str(label_raw).lower() in ("1", "malicious", "spam", "trap") else "normal"

            # Probability score
            score = None
            if hasattr(model, "predict_proba"):
                try:
                    proba = model.predict_proba([text])
                    if proba is not None and len(proba) > 0:
                        score = round(float(proba[0].max()), 4)
                except Exception:
                    score = None

            return PredictResponse(label=label, score=score, tags=tags)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

    # Path 2: Rule-based heuristic fallback if model is not present
    if tags:
        label = "malicious"
        score = round(min(0.95, 0.60 + len(tags) * 0.12), 2)
    else:
        label = "normal"
        score = 0.90

    return PredictResponse(label=label, score=score, tags=tags)

