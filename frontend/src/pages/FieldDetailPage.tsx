import { useState } from "react";
import { useParams } from "react-router-dom";
import FieldMap from "@/components/FieldMap";
import { HealthBadge, SeverityBadge, TreatmentBadge } from "@/components/badges";
import { api } from "@/lib/api";
import {
  useAdvisories,
  useDetections,
  useEnvironmentalRisk,
  useField,
  useFieldHealth,
  useGenerateSprayRecommendations,
  useHotspots,
  useIrrigation,
  useRefreshWeather,
  useTreatmentCoverage,
  useYieldRisk,
  useZones,
} from "@/lib/queries";
import { useQuery } from "@tanstack/react-query";

const TABS = ["Health", "Problems", "Water", "Environment", "Treatment"] as const;
type Tab = (typeof TABS)[number];

export default function FieldDetailPage() {
  const { fieldId } = useParams<{ fieldId: string }>();
  const [tab, setTab] = useState<Tab>("Health");
  const [selectedZoneId, setSelectedZoneId] = useState<string | null>(null);

  const { data: field, isLoading: fieldLoading } = useField(fieldId);
  const { data: zones = [] } = useZones(fieldId);
  const { data: health } = useFieldHealth(fieldId);
  const { data: hotspots = [] } = useHotspots(fieldId);
  const { data: detections = [] } = useDetections(fieldId, {});
  const { data: advisories = [] } = useAdvisories(fieldId);

  if (fieldLoading || !field) {
    return <p className="text-ink/60">Preparing field map...</p>;
  }

  const hectares = field.area_m2 ? (field.area_m2 / 10000).toFixed(2) : null;

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-forest">{field.name}</h1>
          <p className="text-sm text-ink/60">
            {field.crop_type ?? "Crop not set"} {hectares ? `· ${hectares} ha` : ""}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {health && <HealthBadge status={health.status} />}
        </div>
      </div>

      {/* Map */}
      {field.boundary ? (
        <FieldMap
          field={field}
          zones={zones}
          hotspots={hotspots}
          detections={detections}
          onZoneClick={setSelectedZoneId}
          className="h-[360px] sm:h-[440px]"
        />
      ) : (
        <div className="card text-center">No boundary drawn for this field yet.</div>
      )}

      {selectedZoneId && <ZonePanel zoneId={selectedZoneId} onClose={() => setSelectedZoneId(null)} />}

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto border-b border-sand">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`whitespace-nowrap border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
              tab === t ? "border-forest text-forest" : "border-transparent text-ink/50 hover:text-ink"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "Health" && <HealthTab fieldId={field.id} zones={zones} />}
      {tab === "Problems" && <ProblemsTab fieldId={field.id} detections={detections} advisories={advisories} />}
      {tab === "Water" && <WaterTab fieldId={field.id} />}
      {tab === "Environment" && <EnvironmentTab fieldId={field.id} />}
      {tab === "Treatment" && <TreatmentTab fieldId={field.id} />}

      {/* Recent activity */}
      <section className="card">
        <h2 className="mb-3 text-base font-semibold text-forest">Recent activity</h2>
        {detections.length === 0 ? (
          <p className="text-sm text-ink/60">No scans yet. Start a rover scan to begin building your field health map.</p>
        ) : (
          <ul className="divide-y divide-sand">
            {detections.slice(0, 8).map((d) => (
              <li key={d.id} className="flex items-center justify-between gap-3 py-2 text-sm">
                <div className="min-w-0">
                  <p className="text-ink">
                    {d.class_name.replace(/_/g, " ")}
                    {d.zone_code ? ` · Zone ${d.zone_code}` : ""}
                  </p>
                  <p className="text-xs text-ink/50">{new Date(d.created_at).toLocaleString()}</p>
                </div>
                <TreatmentBadge status={d.treatment_status} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function ZonePanel({ zoneId, onClose }: { zoneId: string; onClose: () => void }) {
  const { data: summary } = useQuery({
    queryKey: ["zone-summary", zoneId],
    queryFn: async () => (await api.get(`/zones/${zoneId}/summary`)).data,
  });

  if (!summary) return null;

  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <h3 className="font-semibold text-forest">Zone {summary.code}</h3>
        <button onClick={onClose} className="text-sm text-ink/50 hover:text-ink">
          Close
        </button>
      </div>
      <div className="mt-2 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
        <Stat label="Risk level" value={summary.risk_level} />
        <Stat label="Trend" value={summary.trend} />
        <Stat label="Disease" value={`${summary.disease_prevalence_pct}%`} />
        <Stat label="Pest" value={`${summary.pest_prevalence_pct}%`} />
      </div>
      <p className="mt-3 text-xs text-ink/50">
        {summary.observation_count} observations · {summary.detection_count} detections ·{" "}
        {summary.treatment_status === "TREATED" ? "Treated" : "Not yet treated"}
      </p>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-ink/40">{label}</p>
      <p className="font-medium text-ink">{value}</p>
    </div>
  );
}

function HealthTab({ fieldId, zones }: { fieldId: string; zones: { id: string; code: string }[] }) {
  const { data: health } = useFieldHealth(fieldId);
  const { data: yieldRisk } = useYieldRisk(fieldId);

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <section className="card">
        <h2 className="mb-3 text-base font-semibold text-forest">Field health</h2>
        {health ? (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <HealthBadge status={health.status} />
              <span className="text-sm text-ink/60">Score {health.score}/100</span>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <Stat label="Disease prevalence" value={`${health.disease_prevalence_pct}%`} />
              <Stat label="Pest prevalence" value={`${health.pest_prevalence_pct}%`} />
              <Stat label="Water stress" value={health.water_stress_status} />
              <Stat label="Environmental risk" value={health.environmental_risk} />
            </div>
          </div>
        ) : (
          <p className="text-sm text-ink/60">Loading...</p>
        )}
      </section>

      <section className="card">
        <h2 className="mb-3 text-base font-semibold text-forest">Yield risk</h2>
        {yieldRisk ? (
          <div className="space-y-2">
            <SeverityBadge severity={yieldRisk.yield_risk} />
            {yieldRisk.contributing_factors.length > 0 ? (
              <ul className="mt-2 list-inside list-disc text-sm text-ink/70">
                {yieldRisk.contributing_factors.map((f) => (
                  <li key={f}>{f}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-ink/60">No significant risk factors detected.</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-ink/60">Loading...</p>
        )}
      </section>

      <section className="card lg:col-span-2">
        <h2 className="mb-3 text-base font-semibold text-forest">Zones ({zones.length})</h2>
        <div className="flex flex-wrap gap-1.5">
          {zones.map((z) => (
            <span key={z.id} className="rounded-md border border-sand px-2 py-1 text-xs text-ink/70">
              {z.code}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}

function ProblemsTab({
  fieldId,
  detections,
  advisories,
}: {
  fieldId: string;
  detections: ReturnType<typeof useDetections>["data"];
  advisories: ReturnType<typeof useAdvisories>["data"];
}) {
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <section className="card">
        <h2 className="mb-3 text-base font-semibold text-forest">Current situation</h2>
        {!advisories || advisories.length === 0 ? (
          <p className="text-sm text-ink/60">No active issues right now.</p>
        ) : (
          <ul className="space-y-3">
            {advisories.map((a) => (
              <li key={a.id} className="rounded-lg border border-sand p-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-medium text-ink">{a.what}</p>
                  <SeverityBadge severity={a.severity} />
                </div>
                <p className="text-xs text-ink/50">{a.where_label}</p>
                <p className="mt-2 text-sm text-ink/80">{a.recommended_action}</p>
                <p className="mt-1 text-xs font-medium text-ink/50">
                  {a.action_taken ? "Action already taken" : "Not yet actioned"}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="card">
        <h2 className="mb-3 text-base font-semibold text-forest">Detections</h2>
        {!detections || detections.length === 0 ? (
          <p className="text-sm text-ink/60">No detections recorded yet.</p>
        ) : (
          <ul className="divide-y divide-sand">
            {detections.map((d) => (
              <li key={d.id} className="py-2 text-sm">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-ink">
                    {d.class_name.replace(/_/g, " ")} {d.zone_code ? `· Zone ${d.zone_code}` : ""}
                  </span>
                  <TreatmentBadge status={d.treatment_status} />
                </div>
                <p className="text-xs text-ink/50">
                  Confidence {(d.confidence * 100).toFixed(0)}% · {new Date(d.created_at).toLocaleString()}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function WaterTab({ fieldId }: { fieldId: string }) {
  const { data: irrigation } = useIrrigation(fieldId);
  const refreshWeather = useRefreshWeather(fieldId);

  return (
    <section className="card">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-base font-semibold text-forest">Irrigation</h2>
        <button
          onClick={() => refreshWeather.mutate()}
          disabled={refreshWeather.isPending}
          className="btn-secondary px-3 py-1.5 text-xs"
        >
          {refreshWeather.isPending ? "Syncing weather..." : "Refresh weather"}
        </button>
      </div>
      {irrigation ? (
        <div className="space-y-3">
          <RecommendationBadge value={irrigation.recommendation} />
          <p className="text-sm text-ink/80">{irrigation.reason}</p>
          <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
            <Stat label="Soil moisture" value={irrigation.soil_moisture_pct != null ? `${irrigation.soil_moisture_pct}%` : "—"} />
            <Stat label="Water stress" value={irrigation.water_stress_status} />
            <Stat label="Over-irrigation" value={irrigation.over_irrigation_status} />
            <Stat label="Forecast rain" value={irrigation.forecast_rainfall_mm != null ? `${irrigation.forecast_rainfall_mm}mm` : "—"} />
          </div>
        </div>
      ) : (
        <p className="text-sm text-ink/60">Loading...</p>
      )}
    </section>
  );
}

function EnvironmentTab({ fieldId }: { fieldId: string }) {
  const { data: risk } = useEnvironmentalRisk(fieldId);
  const refreshWeather = useRefreshWeather(fieldId);

  return (
    <section className="card">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-base font-semibold text-forest">Environmental risk</h2>
        <button
          onClick={() => refreshWeather.mutate()}
          disabled={refreshWeather.isPending}
          className="btn-secondary px-3 py-1.5 text-xs"
        >
          {refreshWeather.isPending ? "Syncing weather..." : "Refresh weather"}
        </button>
      </div>
      {risk ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <RiskStat label="Drought" value={risk.drought_risk} />
          <RiskStat label="Flood" value={risk.flood_risk} />
          <RiskStat label="Heat" value={risk.heat_risk} />
          <RiskStat label="Disease-favorable" value={risk.disease_environment_risk} />
        </div>
      ) : (
        <p className="text-sm text-ink/60">Loading...</p>
      )}
    </section>
  );
}

function TreatmentTab({ fieldId }: { fieldId: string }) {
  const { data: coverage } = useTreatmentCoverage(fieldId);
  const generate = useGenerateSprayRecommendations(fieldId);
  const { data: recs = [] } = useQuery({
    queryKey: ["spray-recommendations", fieldId],
    queryFn: async () => (await api.get(`/fields/${fieldId}/spray-recommendations`)).data,
  });

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <section className="card">
        <h2 className="mb-3 text-base font-semibold text-forest">Treatment coverage</h2>
        {coverage ? (
          <div className="grid grid-cols-2 gap-3 text-sm">
            <Stat label="Coverage" value={`${coverage.treatment_coverage_pct}%`} />
            <Stat label="Untreated problems" value={String(coverage.untreated_problem_count)} />
            <Stat label="Qualifying detections" value={String(coverage.qualifying_detections)} />
            <Stat label="Treated" value={String(coverage.treated_detections)} />
          </div>
        ) : (
          <p className="text-sm text-ink/60">Loading...</p>
        )}
      </section>

      <section className="card">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-base font-semibold text-forest">Targeted intervention</h2>
          <button onClick={() => generate.mutate()} disabled={generate.isPending} className="btn-secondary px-3 py-1.5 text-xs">
            {generate.isPending ? "Checking zones..." : "Generate recommendations"}
          </button>
        </div>
        {recs.length === 0 ? (
          <p className="text-sm text-ink/60">No targeted spray recommendations right now.</p>
        ) : (
          <ul className="space-y-2">
            {recs.map((r: any) => (
              <li key={r.id} className="rounded-lg border border-sand p-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-ink">{r.reason}</span>
                  <SeverityBadge severity={r.priority} />
                </div>
                <p className="mt-1 text-xs text-ink/50">{r.status}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function RecommendationBadge({ value }: { value: string }) {
  const styles: Record<string, string> = {
    IRRIGATE_NOW: "bg-risk-critical/15 text-risk-critical",
    IRRIGATE_SOON: "bg-risk-attention/15 text-risk-attention",
    DELAY: "bg-risk-monitor/15 text-risk-monitor",
    NO_IRRIGATION: "bg-risk-healthy/15 text-risk-healthy",
    UNKNOWN: "bg-ink/10 text-ink/60",
  };
  const labels: Record<string, string> = {
    IRRIGATE_NOW: "Irrigate now",
    IRRIGATE_SOON: "Irrigate soon",
    DELAY: "Delay irrigation",
    NO_IRRIGATION: "No irrigation needed",
    UNKNOWN: "Not enough data",
  };
  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1.5 text-sm font-semibold ${styles[value] ?? styles.UNKNOWN}`}>
      {labels[value] ?? value}
    </span>
  );
}

function RiskStat({ label, value }: { label: string; value: string }) {
  const colors: Record<string, string> = {
    NONE: "text-risk-healthy",
    LOW: "text-risk-healthy",
    MODERATE: "text-risk-monitor",
    HIGH: "text-risk-attention",
    CRITICAL: "text-risk-critical",
  };
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-ink/40">{label}</p>
      <p className={`font-semibold ${colors[value] ?? "text-ink"}`}>{value}</p>
    </div>
  );
}
