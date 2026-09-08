import { useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Bar, BarChart } from "recharts";
import { useAllFields, useFarms, useInsights, useTimeSeries, useYieldRisk } from "@/lib/queries";
import { SeverityBadge } from "@/components/badges";

const SECTIONS = ["Crop Health", "Environment", "Operations", "Risk"] as const;
type Section = (typeof SECTIONS)[number];

export default function InsightsPage() {
  const { data: farms } = useFarms();
  const { data: fields } = useAllFields(farms);
  const [fieldId, setFieldId] = useState<string>("");
  const [section, setSection] = useState<Section>("Crop Health");

  useEffect(() => {
    if (!fieldId && fields && fields.length > 0) setFieldId(fields[0].id);
  }, [fields, fieldId]);

  if (fields && fields.length === 0) {
    return <p className="text-ink/60">Add a field to start seeing insights.</p>;
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-bold text-forest">Insights</h1>
        <select value={fieldId} onChange={(e) => setFieldId(e.target.value)} className="input w-auto">
          {fields?.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name}
            </option>
          ))}
        </select>
      </div>

      <div className="flex gap-1 overflow-x-auto border-b border-sand">
        {SECTIONS.map((s) => (
          <button
            key={s}
            onClick={() => setSection(s)}
            className={`whitespace-nowrap border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
              section === s ? "border-forest text-forest" : "border-transparent text-ink/50 hover:text-ink"
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {fieldId && section === "Crop Health" && <CropHealthSection fieldId={fieldId} />}
      {fieldId && section === "Environment" && <EnvironmentSection fieldId={fieldId} />}
      {fieldId && section === "Operations" && <OperationsSection fieldId={fieldId} />}
      {fieldId && section === "Risk" && <RiskSection fieldId={fieldId} />}
    </div>
  );
}

function ChartCard({ title, question, children }: { title: string; question: string; children: React.ReactNode }) {
  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-forest">{title}</h3>
      <p className="mb-2 text-xs text-ink/50">{question}</p>
      <div className="h-48">{children}</div>
    </div>
  );
}

function TrendLine({ fieldId, metric, color }: { fieldId: string; metric: string; color: string }) {
  const { data = [] } = useTimeSeries(fieldId, metric);
  const chartData = data.map((p) => ({ date: new Date(p.timestamp).toLocaleDateString(undefined, { month: "short", day: "numeric" }), value: p.value }));

  if (chartData.length === 0) {
    return <div className="flex h-full items-center justify-center text-xs text-ink/40">No data yet</div>;
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={chartData} margin={{ left: -20, top: 8 }}>
        <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="#8A5A3B" />
        <YAxis tick={{ fontSize: 10 }} stroke="#8A5A3B" allowDecimals={false} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
        <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function TrendBar({ fieldId, metric, color }: { fieldId: string; metric: string; color: string }) {
  const { data = [] } = useTimeSeries(fieldId, metric);
  const chartData = data.map((p) => ({ date: new Date(p.timestamp).toLocaleDateString(undefined, { month: "short", day: "numeric" }), value: p.value }));

  if (chartData.length === 0) {
    return <div className="flex h-full items-center justify-center text-xs text-ink/40">No data yet</div>;
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={chartData} margin={{ left: -20, top: 8 }}>
        <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="#8A5A3B" />
        <YAxis tick={{ fontSize: 10 }} stroke="#8A5A3B" allowDecimals={false} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
        <Bar dataKey="value" fill={color} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function CropHealthSection({ fieldId }: { fieldId: string }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <ChartCard title="Disease detections over time" question="Is the problem increasing or decreasing?">
        <TrendLine fieldId={fieldId} metric="disease" color="#C1502E" />
      </ChartCard>
      <ChartCard title="Pest detections over time" question="Is pest activity spreading?">
        <TrendLine fieldId={fieldId} metric="pest" color="#C89B2E" />
      </ChartCard>
      <ChartCard title="Nutrient deficiency trend" question="Are nutrient issues becoming more common?">
        <TrendLine fieldId={fieldId} metric="nutrient" color="#7A7550" />
      </ChartCard>
    </div>
  );
}

function EnvironmentSection({ fieldId }: { fieldId: string }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <ChartCard title="Soil moisture" question="Is the field becoming too dry?">
        <TrendLine fieldId={fieldId} metric="soil_moisture" color="#2B5039" />
      </ChartCard>
      <ChartCard title="Temperature" question="Is heat stress building up?">
        <TrendLine fieldId={fieldId} metric="temperature" color="#D97B2B" />
      </ChartCard>
      <ChartCard title="Humidity" question="Are conditions favorable for disease?">
        <TrendLine fieldId={fieldId} metric="humidity" color="#4C7A3F" />
      </ChartCard>
    </div>
  );
}

function OperationsSection({ fieldId }: { fieldId: string }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <ChartCard title="Irrigation history" question="How often has this field been irrigated?">
        <TrendBar fieldId={fieldId} metric="irrigation" color="#2B5039" />
      </ChartCard>
      <ChartCard title="Treatment history" question="How often has this field been treated?">
        <TrendBar fieldId={fieldId} metric="treatment" color="#8A5A3B" />
      </ChartCard>
    </div>
  );
}

function RiskSection({ fieldId }: { fieldId: string }) {
  const { data: yieldRisk } = useYieldRisk(fieldId);
  const { data: insights = [] } = useInsights(fieldId);

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div className="card">
        <h3 className="mb-2 text-sm font-semibold text-forest">Yield risk indicator</h3>
        {yieldRisk ? (
          <>
            <SeverityBadge severity={yieldRisk.yield_risk} />
            <ul className="mt-3 list-inside list-disc text-sm text-ink/70">
              {yieldRisk.contributing_factors.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
          </>
        ) : (
          <p className="text-sm text-ink/60">Loading...</p>
        )}
      </div>

      <div className="card">
        <h3 className="mb-2 text-sm font-semibold text-forest">What's changing</h3>
        {insights.length === 0 ? (
          <p className="text-sm text-ink/60">Nothing significant to flag right now.</p>
        ) : (
          <ul className="space-y-2">
            {insights.map((i, idx) => (
              <li key={idx} className="rounded-lg border border-sand p-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-ink">{i.message}</span>
                  <SeverityBadge severity={i.severity} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
