import { useRef, useState } from "react";
import { checkLeafImage, LeafCheckError, parseLabel, type LeafCheckResult } from "./api";

type Status = "idle" | "loading" | "done" | "error";

export default function LeafCheckPage() {
  const [status, setStatus] = useState<Status>("idle");
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<LeafCheckResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File | undefined) {
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError(null);
    setStatus("loading");
    try {
      const res = await checkLeafImage(file);
      setResult(res);
      setStatus("done");
    } catch (err) {
      setError(err instanceof LeafCheckError ? err.message : "Something went wrong. Try again.");
      setStatus("error");
    }
  }

  function reset() {
    setStatus("idle");
    setResult(null);
    setError(null);
    setPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  const top = result ? parseLabel(result.predicted_class) : null;

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div>
        <h1 className="text-xl font-bold text-forest">Leaf Check</h1>
        <p className="mt-1 text-sm text-ink/70">
          Not near the rover, or want a second opinion? Upload a close-up photo of an eggplant leaf and get an
          instant read on what might be affecting it.
        </p>
        <p className="mt-1 text-xs text-ink/50">Currently trained on eggplant leaves only.</p>
      </div>

      <div className="card">
        <div
          className="flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-sand bg-sand/30 px-4 py-10 text-center"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            handleFile(e.dataTransfer.files?.[0]);
          }}
        >
          {preview ? (
            <img src={preview} alt="Uploaded leaf" className="h-48 w-48 rounded-lg object-cover shadow-card" />
          ) : (
            <LeafPhotoIcon className="h-12 w-12 text-forest/40" />
          )}

          <div className="flex flex-col items-center gap-2">
            <button type="button" onClick={() => fileInputRef.current?.click()} className="btn-primary">
              {preview ? "Choose a different photo" : "Upload a leaf photo"}
            </button>
            <p className="text-xs text-ink/50">JPG, PNG or WEBP · one leaf, filling most of the frame, in good light</p>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
        </div>

        {status === "loading" && (
          <p className="mt-4 text-center text-sm text-ink/60">Reading the leaf image...</p>
        )}

        {status === "error" && error && (
          <div className="mt-4 rounded-lg bg-risk-critical/10 px-4 py-3 text-sm text-risk-critical">{error}</div>
        )}

        {status === "done" && result && top && (
          <div className="mt-5 space-y-4">
            <div
              className={`rounded-xl border p-4 ${
                top.healthy ? "border-risk-healthy/30 bg-risk-healthy/10" : "border-risk-attention/30 bg-risk-attention/10"
              }`}
            >
              <p className="text-xs font-medium uppercase tracking-wide text-ink/50">Crop</p>
              <p className="text-lg font-bold text-ink">{top.crop}</p>
              <p className="mt-2 text-xs font-medium uppercase tracking-wide text-ink/50">
                {top.healthy ? "Condition" : "Possible issue"}
              </p>
              <p className={`text-lg font-bold ${top.healthy ? "text-risk-healthy" : "text-risk-attention"}`}>
                {top.condition}
              </p>
              <p className="mt-2 text-sm text-ink/70">Confidence: {(result.confidence * 100).toFixed(0)}%</p>
            </div>

            <p className="rounded-lg bg-sand/60 px-3 py-2 text-xs text-ink/60">
              This is an automated estimate from a photo, not a confirmed diagnosis. Inspect the plant closely, and
              treat it the same way you would a rover detection — confirm before acting.
            </p>

            {result.top_predictions.length > 1 && (
              <div>
                <p className="mb-2 text-xs font-medium uppercase tracking-wide text-ink/50">Other possibilities</p>
                <ul className="space-y-1.5">
                  {result.top_predictions.slice(1).map((p, i) => {
                    const alt = parseLabel(p.label);
                    return (
                      <li key={i} className="flex items-center justify-between text-sm text-ink/70">
                        <span>
                          {alt.crop} — {alt.condition}
                        </span>
                        <span className="text-ink/40">{(p.confidence * 100).toFixed(0)}%</span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}

            <button type="button" onClick={reset} className="btn-secondary w-full">
              Check another photo
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function LeafPhotoIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path
        d="M5 19c8 0 14-6 14-14 0 0-12-1-14 8-1 4 0 6 0 6Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path d="M5 19c0-4 2-8 6-10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}
