# Plant Disease Classifier — isolated experiment

**This folder is completely separate from the main application.** It has its
own virtual environment, its own port, and its own dependencies. Nothing in
`backend/` or `frontend/` was touched or imports anything from here.

**To remove this feature entirely:** delete this folder. Nothing else breaks.

Uses the pretrained Hugging Face checkpoint
[`Kathir56/plant-disease-tamilnadu`](https://huggingface.co/Kathir56/plant-disease-tamilnadu)
as-is — no training, fine-tuning, or weight changes. It's a MobileNetV2
classifier over 38 PlantVillage classes (disease + healthy states for tomato,
potato, corn, grape, apple, pepper, etc).

## What you need to do (nothing, actually)

The model is public on the Hugging Face Hub — no account, API key, or token
required. It downloaded and ran successfully with zero credentials. The only
optional thing: if you later hit Hugging Face's anonymous rate limit (very
unlikely for casual local testing), you could set a free `HF_TOKEN` env var,
but this wasn't needed and isn't required to use what's built here.

## 1. Packages required

Already installed in this folder's own `.venv` — see `requirements.txt`:

- `torch` (CPU build, via PyTorch's own package index)
- `transformers` (loads the model + runs inference)
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

First startup downloads the model checkpoint from Hugging Face (a few
seconds — it's a small MobileNetV2). Subsequent startups load it from the
local Hugging Face cache, no network needed.

Server: `http://127.0.0.1:8020` · health check: `GET /health`

## 3. Test it with one image

```bash
curl -X POST http://127.0.0.1:8020/predict \
  -F "file=@/path/to/your/leaf.jpg;type=image/jpeg"
```

Response shape:

```json
{
  "predicted_class": "Tomato___Late_blight",
  "confidence": 0.95,
  "top_predictions": [
    {"label": "Tomato___Late_blight", "confidence": 0.95},
    {"label": "Tomato___Early_blight", "confidence": 0.03},
    {"label": "Tomato___healthy", "confidence": 0.01}
  ]
}
```

Verified working end-to-end with a real HTTP request during setup (see below —
result is nonsense because the test image was a plain solid-color square,
not a real leaf; that's expected, it only proves the pipeline works).

```
$ curl -X POST http://127.0.0.1:8020/predict -F "file=@sample_leaf.jpg;type=image/jpeg"
{"predicted_class": "Tomato___Late_blight", "confidence": 0.2346, ...}
```

Use a real photo of a leaf for a meaningful prediction.

## 4. How your existing frontend *would* call this

Shown here as reference only — **not wired into the real app**. If you
decide to integrate for real later, this is the shape of it:

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

```tsx
// Example usage in a React component
<input
  type="file"
  accept="image/*"
  onChange={async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const result = await classifyLeaf(file);
    console.log(result.predicted_class, result.confidence);
  }}
/>
```

## Files in this folder

- `inference.py` — loads the model, runs a single prediction
- `app.py` — FastAPI `/predict` and `/health` endpoints
- `requirements.txt` — isolated dependencies
- `sample_leaf.jpg` — synthetic placeholder image used only to smoke-test the
  pipeline (not a real leaf; delete freely)
- `server.log` — local dev server output (gitignored)
