from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import joblib
import os

app = FastAPI(title="WhatsApp Malicious Message Detector")

# Allow CORS for extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev mode; restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "honeytrap_detector.joblib")

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    label: str
    score: Optional[float] = None
    tags: List[str] = []

try:
    model = joblib.load(MODEL_PATH)
    load_error = None
except Exception as e:
    model = None
    load_error = str(e)


@app.get("/")
def root():
    if model is None:
        return {"status": f"model failed to load: {load_error}"}
    return {"status": "model loaded"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=500, detail=f"Model not loaded: {load_error}")

    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text provided")

    try:
        pred = model.predict([text])
        label_raw = pred[0]

        # Normalize label
        if isinstance(label_raw, (int, float)):
            label = "malicious" if int(label_raw) == 1 else "normal"
        else:
            label = "malicious" if str(label_raw).lower() in ("1", "malicious", "spam") else "normal"

        # Score
        score = None
        if hasattr(model, "predict_proba"):
            try:
                proba = model.predict_proba([text])
                if proba is not None and len(proba) > 0:
                    score = float(proba[0].max())
            except Exception:
                score = None

        # Simple keyword-based tagging
        tags = []
        lowered = text.lower()
        if any(w in lowered for w in ["urgent", "asap", "hurry", "now"]):
            tags.append("urgency")
        if any(w in lowered for w in ["baby", "dear", "love", "flirt", "kiss"]):
            tags.append("flirty")
        if any(w in lowered for w in ["trust", "secret", "don’t tell", "only you"]):
            tags.append("manipulation")

        return PredictResponse(label=label, score=score, tags=tags)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
