"""Standalone FastAPI service exposing the pretrained plant-disease classifier.

Deliberately isolated from the main Smart Farming Assistant backend/frontend —
its own venv, its own port, its own folder. Delete this whole folder to remove
the experiment with zero impact on the rest of the app.
"""
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from inference import MODEL_NAME, get_classifier, predict

app = FastAPI(title="Eggplant Leaf Disease Classifier (experiment)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # experiment only — tighten before any real integration
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


class PredictionItem(BaseModel):
    label: str
    confidence: float


class PredictResponse(BaseModel):
    predicted_class: str
    confidence: float
    top_predictions: list[PredictionItem]


@app.on_event("startup")
def warm_up():
    # Loads the model checkpoint once at startup instead of on the first
    # request, so the first real prediction isn't slow.
    get_classifier()


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/predict", response_model=PredictResponse)
async def predict_endpoint(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {file.content_type}")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        results = predict(image_bytes, top_k=3)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=f"Could not read this as an image: {exc}")

    top = results[0]
    return PredictResponse(
        predicted_class=top["label"],
        confidence=top["confidence"],
        top_predictions=[PredictionItem(**r) for r in results],
    )
