"""Loads the pretrained eggplant-leaf-disease checkpoint trained by a teammate
and exposes a predict() function. No training, fine-tuning, or weight
modification happens here — this only loads the existing checkpoint file and
runs it for inference.

Source: https://github.com/Pragkya/Plant-Detection (MobileNetV2 transfer
learning, frozen ImageNet backbone, trained on eggplant leaf images).
"""
from functools import lru_cache
from io import BytesIO
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image

MODEL_NAME = "eggplant-mobilenetv2 (Pragkya/Plant-Detection)"
MODEL_PATH = Path(__file__).parent / "model" / "best_mobilenetv2.keras"
IMG_SIZE = (224, 224)

# Order matches tf.keras.utils.image_dataset_from_directory's alphabetical
# subfolder sort during training (train.py) — must not be reordered.
CLASS_NAMES = [
    "Healthy Leaf",
    "Insect Pest Disease",
    "Leaf Spot Disease",
    "Mosaic Virus Disease",
    "Small Leaf Disease",
    "White Mold Disease",
    "Wilt Disease",
]


@lru_cache(maxsize=1)
def get_classifier():
    """Lazily loads the model once per process and caches it in memory."""
    return tf.keras.models.load_model(MODEL_PATH)


def predict(image_bytes: bytes, top_k: int = 3) -> list[dict]:
    image = Image.open(BytesIO(image_bytes)).convert("RGB").resize(IMG_SIZE)
    # No manual normalization here — tf.keras.applications.mobilenet_v2.preprocess_input
    # is baked into the model graph itself (see train.py), so raw 0-255 pixel
    # values are what the model expects.
    img_array = np.expand_dims(np.array(image), axis=0)

    model = get_classifier()
    predictions = model.predict(img_array, verbose=0)[0]

    ranked_indices = sorted(range(len(CLASS_NAMES)), key=lambda i: predictions[i], reverse=True)[:top_k]
    return [{"label": CLASS_NAMES[i], "confidence": round(float(predictions[i]), 4)} for i in ranked_indices]


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python inference.py <path-to-image>")
        raise SystemExit(1)

    with open(sys.argv[1], "rb") as f:
        data = f.read()

    for r in predict(data):
        print(f"{r['label']}: {r['confidence']:.2%}")
