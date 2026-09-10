# Plant Disease Classifier — isolated experiment

**This folder is completely separate from the main application.** It has its
own virtual environment, its own port, and its own dependencies. Nothing in
`backend/` or `frontend/` was touched or imports anything from here — the
frontend's Leaf Check feature just calls this service's HTTP API.

**To remove this feature entirely:** delete this folder. Nothing else breaks.

## Model

Uses a pretrained checkpoint trained by a teammate, published at
[`Pragkya/Plant-Detection`](https://github.com/Pragkya/Plant-Detection) — no
training, fine-tuning, or weight changes happen here, only inference. It's a
MobileNetV2 (frozen ImageNet backbone, transfer learning) trained on
**eggplant leaves only**, over 7 classes:

- Healthy Leaf
- Insect Pest Disease
- Leaf Spot Disease
- Mosaic Virus Disease
- Small Leaf Disease
- White Mold Disease
- Wilt Disease

Reported accuracy in the source repo: ~91.8% on held-out (non-augmented) test
images. This is narrower than the previous Hugging Face model used here
(`Kathir56/plant-disease-tamilnadu`, 38 classes across tomato/potato/corn/
grape/apple/pepper/etc) — this one is eggplant-specific. The checkpoint file
(`model/best_mobilenetv2.keras`, ~9.3MB) is committed directly in this repo,
copied from the source project (no Git LFS involved on either side).

## What you need to do (nothing, actually)

The checkpoint is already committed in `model/best_mobilenetv2.keras` — no
download, account, or API key needed. It's loaded straight from disk on
startup.

## 1. Packages required

Already installed in this folder's own `.venv` — see `requirements.txt`:

- `tensorflow` (loads the `.keras` checkpoint + runs inference)
- `pillow` (image decoding)
- `fastapi`, `uvicorn[standard]`, `python-multipart` (the HTTP API)

## 2. Run it locally

```bash
cd experiments/plant_disease_classifier
python -m venv .venv
.venv\Scripts\activate          # Windows Command Prompt
# or: source .venv/Scripts/activate   (Git Bash)
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8020
```

Server: `http://127.0.0.1:8020` · health check: `GET /health`

## 3. Test it with one image

```bash
curl -X POST http://127.0.0.1:8020/predict \
  -F "file=@/path/to/your/eggplant-leaf.jpg;type=image/jpeg"
```

Response shape (unchanged from before, so the frontend integration didn't
need to change its request/response handling — only its label-parsing logic,
since these labels are already plain strings like `"Leaf Spot Disease"`
rather than the old PlantVillage `"Crop___Condition"` format):

```json
{
  "predicted_class": "Leaf Spot Disease",
  "confidence": 0.4851,
  "top_predictions": [
    {"label": "Leaf Spot Disease", "confidence": 0.4851},
    {"label": "Mosaic Virus Disease", "confidence": 0.314},
    {"label": "White Mold Disease", "confidence": 0.1673}
  ]
}
```

Verified working end-to-end with a real HTTP request during setup (see
below — result is unreliable because the test image is a synthetic
placeholder, not a real leaf; that's expected, it only proves the pipeline
works end-to-end):

```
$ curl -X POST http://127.0.0.1:8020/predict -F "file=@sample_leaf.jpg;type=image/jpeg"
{"predicted_class": "Leaf Spot Disease", "confidence": 0.4851, ...}
```

Use a real photo of an eggplant leaf for a meaningful prediction.

## 4. How the frontend calls this

Wired into the main app's Leaf Check page —
`frontend/src/features/leaf-check/api.ts` — which talks directly to this
service's `/predict` endpoint (no auth token, separate from the main
backend's axios client):

```ts
async function classifyLeaf(file: File) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch("http://127.0.0.1:8020/predict", {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error("Prediction failed");
  return res.json(); // { predicted_class, confidence, top_predictions }
}
```

## Files in this folder

- `model/best_mobilenetv2.keras` — the committed trained checkpoint
- `inference.py` — loads the model, runs a single prediction
- `app.py` — FastAPI `/predict` and `/health` endpoints
- `requirements.txt` — isolated dependencies
- `sample_leaf.jpg` — synthetic placeholder image used only to smoke-test the
  pipeline (not a real leaf; delete freely)
- `server.log` — local dev server output (gitignored)

## Source repo details (for reference)

Investigated directly from a clone of `Pragkya/Plant-Detection`:

- Framework: TensorFlow/Keras (`tf.keras.models.load_model`), not PyTorch/ONNX.
- Preprocessing: resize to 224×224 RGB, raw 0–255 pixel values (no manual
  normalization — `mobilenet_v2.preprocess_input` is baked into the model
  graph itself as its first layer, so double-normalizing would be wrong).
- Class order matches `tf.keras.utils.image_dataset_from_directory`'s
  alphabetical subfolder sort — the list in `inference.py` must stay in that
  exact order.
- Two checkpoints existed in the source repo (`best_mobilenetv2.keras`, the
  best validation-accuracy checkpoint, and `eggplant_mobilenetv2.keras`, the
  final epoch after early stopping) — this integration uses `best_*`, the one
  the source repo's own demo (`dashboard.py`) uses.
