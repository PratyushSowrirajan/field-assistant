// Deliberately separate from src/lib/api.ts — this talks to the standalone
// classifier service (experiments/plant_disease_classifier), not the main
// backend. No auth token, no shared axios instance. See README.md.

const CLASSIFIER_BASE_URL = import.meta.env.VITE_LEAF_CHECK_API_URL || "http://127.0.0.1:8020";

export interface LeafPrediction {
  label: string;
  confidence: number;
}

export interface LeafCheckResult {
  predicted_class: string;
  confidence: number;
  top_predictions: LeafPrediction[];
}

export class LeafCheckError extends Error {}

export async function checkLeafImage(file: File): Promise<LeafCheckResult> {
  const form = new FormData();
  form.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${CLASSIFIER_BASE_URL}/predict`, {
      method: "POST",
      body: form,
    });
  } catch {
    throw new LeafCheckError(
      "Couldn't reach the leaf-check service. Make sure it's running (see experiments/plant_disease_classifier/README.md)."
    );
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new LeafCheckError(body?.detail || "Couldn't read this image. Try another photo.");
  }

  return response.json();
}

/** The classifier is currently trained on eggplant leaves only (see
 * experiments/plant_disease_classifier/README.md) — its labels are already
 * plain human-readable strings like "Leaf Spot Disease" or "Healthy Leaf",
 * with no crop prefix, so there's no PlantVillage-style "Crop___Condition"
 * splitting needed here anymore. */
export function parseLabel(label: string): { crop: string; condition: string; healthy: boolean } {
  const healthy = label.toLowerCase().includes("healthy");
  return { crop: "Eggplant", condition: label, healthy };
}
