# Leaf Check (isolated, removable feature)

Lets a farmer upload a photo of a leaf and get an instant disease/pest read,
without needing the rover. Backed by the standalone classifier service in
`experiments/plant_disease_classifier/` (a pretrained Hugging Face model,
not connected to the main database, zones, or alert pipeline).

This folder is deliberately self-contained so it can be deleted with almost
no trace:

## What's isolated here
- `api.ts` — its own tiny HTTP client, pointed at `VITE_LEAF_CHECK_API_URL`
  (the classifier service, default `http://127.0.0.1:8020`). It does **not**
  use the main app's `lib/api.ts` axios instance or auth token.
- `LeafCheckPage.tsx` — the whole page/UI.
- Results are shown to the farmer only. Nothing is written to the main
  backend's database — no CNNDetection row, no Alert, no Advisory. It is a
  separate, farmer-driven "check it yourself" tool alongside the rover, not
  part of the rover's automated detection pipeline.

## The only two touch points in the rest of the app
1. One route in `src/App.tsx`: `<Route path="/leaf-check" element={<LeafCheckPage />} />`
2. One nav entry in `src/components/Layout.tsx`'s `NAV_ITEMS`.

## To remove this feature entirely
1. Delete this folder (`src/features/leaf-check/`).
2. Delete the one route line in `App.tsx` and the one nav entry in `Layout.tsx`.
3. Remove `VITE_LEAF_CHECK_API_URL` from `frontend/.env` / `.env.example`.
4. Stop running / delete `experiments/plant_disease_classifier/`.

No other file in the app references this feature.
