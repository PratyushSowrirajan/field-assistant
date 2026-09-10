"""Loads the pretrained Kathir56/plant-disease-tamilnadu checkpoint from the
Hugging Face Hub and exposes a predict() function. No training, fine-tuning,
or weight modification happens here — this only downloads and runs the
existing checkpoint for inference.
"""
from functools import lru_cache
from io import BytesIO

from PIL import Image
from transformers import pipeline

MODEL_ID = "Kathir56/plant-disease-tamilnadu"


@lru_cache(maxsize=1)
def get_classifier():
    """Lazily loads the model once per process and caches it in memory."""
    return pipeline("image-classification", model=MODEL_ID)


def predict(image_bytes: bytes, top_k: int = 3) -> list[dict]:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    classifier = get_classifier()
    results = classifier(image, top_k=top_k)
    # transformers returns [{"label": ..., "score": ...}, ...] already sorted by score
    return [{"label": r["label"], "confidence": round(float(r["score"]), 4)} for r in results]


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python inference.py <path-to-image>")
        raise SystemExit(1)

    with open(sys.argv[1], "rb") as f:
        data = f.read()

    for r in predict(data):
        print(f"{r['label']}: {r['confidence']:.2%}")
