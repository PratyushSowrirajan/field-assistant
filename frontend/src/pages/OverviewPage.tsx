import { useState } from "react";
import { Link } from "react-router-dom";
import { HealthBadge } from "@/components/badges";
import { HealthRing, NutrientGauge, TrendArrow } from "@/components/Gauges";
import { useAllFields, useFarms, useFieldOverview } from "@/lib/queries";

const NUTRIENT_DISPLAY_MAX: Record<string, number> = {
  NITROGEN: 130,
  PHOSPHORUS: 65,
  POTASSIUM: 320,
};

const STATUS_STYLES: Record<string, string> = {
  LOW: "bg-risk-attention/15 text-risk-attention",
  OPTIMAL: "bg-risk-healthy/15 text-risk-healthy",
  HIGH: "bg-risk-critical/15 text-risk-critical",
  UNKNOWN: "bg-ink/10 text-ink/50",
};

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const mins = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 60000));
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.round(mins / 60);
  return `${hrs} hr${hrs > 1 ? "s" : ""} ago`;
}

export default function OverviewPage() {
  const { data: farms } = useFarms();
  const { data: allFields } = useAllFields(farms);
  const fields = (allFields ?? []).filter((f) => !f.archived);
  const [fieldId, setFieldId] = useState<string | undefined>(undefined);
  const activeFieldId = fieldId ?? fields[0]?.id;
  const field = fields.find((f) => f.id === activeFieldId);

  const { data: overview, isLoading } = useFieldOverview(activeFieldId);

  if (farms && fields.length === 0) {
    return (
      <div className="card mx-auto max-w-md text-center">
        <p className="font-medium text-ink">No fields yet</p>
        <p className="mt-1 text-sm text-ink/60">Add a field to see its live overview here.</p>
        <Link to="/fields/new" className="btn-primary mt-4 inline-flex">
          Add a field
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-bold text-forest">Overview</h1>
        <div className="flex items-center gap-3">
          {fields.length > 1 && (
            <select
              value={activeFieldId ?? ""}
              onChange={(e) => setFieldId(e.target.value)}
              className="input w-auto"
            >
              {fields.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.name}
                </option>
              ))}
            </select>
          )}
          <ConnectionPill status={overview?.connection_status} />
        </div>
      </div>

      {isLoading && <p className="text-ink/60">Loading field overview...</p>}

      {overview && field && (
        <>
          {/* Field header + health */}
          <div className="card flex flex-wrap items-center gap-5 sm:flex-nowrap">
            <HealthRing score={overview.health_score} status={overview.health_status} />
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium uppercase tracking-wide text-ink/50">
                {overview.farm_name} · Field
              </p>
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-2xl font-bold text-ink">{overview.crop_type ?? field.name}</h2>
                <HealthBadge status={overview.health_status} />
              </div>
              <p className="mt-1 text-sm text-ink/60">
                {field.name}
                {overview.growth_stage ? ` · ${overview.growth_stage}` : ""}
                {overview.area_m2 ? ` · ${(overview.area_m2 / 10000).toFixed(2)} ha` : ""}
              </p>
              <p className="mt-1 text-xs text-ink/50">
                {overview.last_scan_at ? `Last rover scan ${timeAgo(overview.last_scan_at)}` : "No rover scans yet"}
              </p>
              <Link to={`/fields/${field.id}`} className="mt-2 inline-block text-sm font-medium text-forest hover:underline">
                Open full field detail →
              </Link>
            </div>
          </div>

          {/* Latest AI prediction */}
          <div className="card">
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-base font-semibold text-forest">Latest AI prediction</h2>
              {overview.latest_prediction?.confidence_label && (
                <span className="rounded-full bg-sand px-2.5 py-1 text-xs font-semibold text-ink/70">
                  {(overview.latest_prediction.confidence! * 100).toFixed(0)}% · {overview.latest_prediction.confidence_label}
                </span>
              )}
            </div>
            {overview.latest_prediction ? (
              <>
                <p className="text-lg font-bold text-ink">{overview.latest_prediction.class_label}</p>
                <p className="text-sm text-ink/50">
                  {overview.latest_prediction.zone_code ? `Zone ${overview.latest_prediction.zone_code} · ` : ""}
                  {timeAgo(overview.last_scan_at)}
                </p>
                <p className="mt-2 rounded-lg bg-sand/60 px-3 py-2 text-sm text-ink/80">
                  {overview.latest_prediction.message}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Link to="/leaf-check" className="btn-primary px-4 py-2 text-sm">
                    Scan another leaf
                  </Link>
                  <Link to={`/fields/${field.id}`} className="btn-secondary px-4 py-2 text-sm">
                    View field history
                  </Link>
                </div>
              </>
            ) : (
              <p className="text-sm text-ink/60">
                No scans yet.{" "}
                <Link to="/leaf-check" className="font-medium text-forest hover:underline">
                  Check a leaf yourself
                </Link>{" "}
                or send the rover out to start building this field's history.
              </p>
            )}
          </div>

          {/* Environment tiles */}
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {overview.environment.map((tile) => (
              <div key={tile.label} className="card">
                <div className="flex items-start justify-between">
                  <p className="text-3xl font-bold text-ink">
                    {tile.value === null ? "—" : tile.value.toFixed(1)}
                    <span className="text-base font-medium text-ink/50">{tile.unit}</span>
                  </p>
                  <TrendArrow trend={tile.trend} />
                </div>
                <p className="mt-1 text-xs font-medium uppercase tracking-wide text-ink/50">{tile.label}</p>
              </div>
            ))}
          </div>

          {/* Nutrients */}
          <div>
            <h2 className="mb-2 text-base font-semibold text-forest">Soil nutrients</h2>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              {overview.nutrients.map((n) => (
                <div key={n.nutrient} className="card">
                  <div className="mb-1 flex items-center justify-between">
                    <p className="text-xs font-medium uppercase tracking-wide text-ink/50">{n.label}</p>
                    <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${STATUS_STYLES[n.status]}`}>
                      {n.status}
                    </span>
                  </div>
                  <NutrientGauge value={n.value} displayMax={NUTRIENT_DISPLAY_MAX[n.nutrient]} unit="" />
                  <p className="text-center text-xs text-ink/50">
                    {n.value === null
                      ? "No reading yet"
                      : `${n.delta_vs_previous ? (n.delta_vs_previous > 0 ? "+" : "") + n.delta_vs_previous.toFixed(1) + " " : ""}${n.unit} vs last`}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function ConnectionPill({ status }: { status?: string }) {
  if (!status) return null;
  const map: Record<string, { label: string; dot: string; text: string }> = {
    CONNECTED: { label: "Live", dot: "bg-leaf", text: "text-leaf-dark" },
    OFFLINE: { label: "Rover offline", dot: "bg-ink/30", text: "text-ink/50" },
    NO_ROVER: { label: "No rover assigned", dot: "bg-ink/20", text: "text-ink/40" },
  };
  const s = map[status] ?? map.NO_ROVER;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full bg-sand px-3 py-1 text-xs font-semibold ${s.text}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
      {s.label}
    </span>
  );
}
