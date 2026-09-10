import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import FieldBoundaryMap from "@/components/FieldBoundaryMap";
import { api } from "@/lib/api";
import { useFarms } from "@/lib/queries";

export default function NewFieldPage() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { data: farms } = useFarms();
  const [farmId, setFarmId] = useState<string>("");
  const [points, setPoints] = useState<[number, number][]>([]);
  const [name, setName] = useState("");
  const [cropType, setCropType] = useState("");
  const [cropVariety, setCropVariety] = useState("");
  const [plantingDate, setPlantingDate] = useState("");
  const [resolution, setResolution] = useState(10);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const effectiveFarmId = farmId || farms?.[0]?.id || "";
  const canSave = points.length >= 3 && name.trim().length > 0 && !!effectiveFarmId;

  function undoPoint() {
    setPoints((p) => p.slice(0, -1));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!canSave) return;
    setSubmitting(true);
    setError(null);
    try {
      const ring = [...points, points[0]];
      const res = await api.post(`/farms/${effectiveFarmId}/fields`, {
        name,
        crop_type: cropType || null,
        crop_variety: cropVariety || null,
        planting_date: plantingDate || null,
        zone_resolution_m: resolution,
        boundary: { type: "Polygon", coordinates: [ring] },
      });
      navigate(`/fields/${res.data.id}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || t("newField.couldNotSave"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold text-forest">{t("newField.title")}</h1>
        <p className="text-sm text-ink/60">{t("newField.subtitle")}</p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_380px]">
        <div className="h-[420px] overflow-hidden rounded-xl2 border border-sand shadow-card sm:h-[520px]">
          <FieldBoundaryMap points={points} onAddPoint={(p) => setPoints((prev) => [...prev, p])} />
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-ink/60">{t("newField.pointsMarked", { count: points.length })}</span>
            <div className="flex gap-2">
              <button type="button" onClick={undoPoint} disabled={!points.length} className="btn-secondary px-3 py-1.5 text-xs">
                {t("newField.undoPoint")}
              </button>
              <button type="button" onClick={() => setPoints([])} disabled={!points.length} className="btn-secondary px-3 py-1.5 text-xs">
                {t("newField.clear")}
              </button>
            </div>
          </div>

          {farms && farms.length > 1 && (
            <label className="block">
              <span className="mb-1 block text-sm font-medium text-ink/80">{t("newField.farm")}</span>
              <select value={effectiveFarmId} onChange={(e) => setFarmId(e.target.value)} className="input">
                {farms.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name}
                  </option>
                ))}
              </select>
            </label>
          )}

          <label className="block">
            <span className="mb-1 block text-sm font-medium text-ink/80">{t("newField.fieldName")}</span>
            <input
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input"
              placeholder={t("newField.fieldNamePlaceholder")}
            />
          </label>

          <label className="block">
            <span className="mb-1 block text-sm font-medium text-ink/80">{t("newField.crop")}</span>
            <input
              value={cropType}
              onChange={(e) => setCropType(e.target.value)}
              className="input"
              placeholder={t("newField.cropPlaceholder")}
            />
          </label>

          <label className="block">
            <span className="mb-1 block text-sm font-medium text-ink/80">{t("newField.varietyOptional")}</span>
            <input value={cropVariety} onChange={(e) => setCropVariety(e.target.value)} className="input" />
          </label>

          <label className="block">
            <span className="mb-1 block text-sm font-medium text-ink/80">{t("newField.plantingDateOptional")}</span>
            <input type="date" value={plantingDate} onChange={(e) => setPlantingDate(e.target.value)} className="input" />
          </label>

          <label className="block">
            <span className="mb-1 block text-sm font-medium text-ink/80">{t("newField.zoneSize")}</span>
            <select value={resolution} onChange={(e) => setResolution(Number(e.target.value))} className="input">
              <option value={5}>{t("newField.zoneFine")}</option>
              <option value={10}>{t("newField.zoneDefault")}</option>
              <option value={20}>{t("newField.zoneCoarse")}</option>
            </select>
          </label>

          {error && <p className="text-sm text-risk-critical">{error}</p>}

          <button type="submit" disabled={!canSave || submitting} className="btn-primary w-full">
            {submitting ? t("newField.savingField") : t("newField.saveField")}
          </button>
          {points.length > 0 && points.length < 3 && (
            <p className="text-xs text-ink/50">{t("newField.markAtLeast3")}</p>
          )}
        </form>
      </div>
    </div>
  );
}
