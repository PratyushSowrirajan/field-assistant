import type { Trend } from "@/types/api";

const RISK_COLORS: Record<string, string> = {
  HEALTHY: "#4C7A3F", // leaf
  MONITOR: "#C89B2E",
  ATTENTION: "#D97B2B",
  HIGH_RISK: "#C1502E",
  CRITICAL: "#A32F26",
};

const NEEDS_ATTENTION = new Set(["ATTENTION", "HIGH_RISK", "CRITICAL"]);

/** Circular "health score" ring, e.g. the 78/100 dial on the field header. */
export function HealthRing({ score, status }: { score: number; status: string }) {
  const clamped = Math.max(0, Math.min(100, score));
  const color = RISK_COLORS[status] ?? RISK_COLORS.MONITOR;
  const r = 42;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - clamped / 100);
  const urgent = NEEDS_ATTENTION.has(status);

  return (
    <div className={`relative h-28 w-28 shrink-0 ${urgent ? "animate-pulse" : ""}`}>
      <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#F1E9D8" strokeWidth="10" />
        <circle
          cx="50"
          cy="50"
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.8s ease" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-ink">{Math.round(clamped)}</span>
        <span className="text-[10px] font-medium uppercase tracking-wide text-ink/50">Health</span>
      </div>
    </div>
  );
}

/** Small line-and-fill chart of recent readings — the actual "how is it changing" signal. */
export function Sparkline({
  values,
  color,
  height = 32,
  width = 120,
}: {
  values: number[];
  color: string;
  height?: number;
  width?: number;
}) {
  if (values.length < 2) {
    return <div style={{ height }} className="flex items-center text-[11px] text-ink/30">Not enough data yet</div>;
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const pad = 4;
  const step = (width - pad * 2) / (values.length - 1);

  const points = values.map((v, i) => {
    const x = pad + i * step;
    const y = pad + (1 - (v - min) / span) * (height - pad * 2);
    return [x, y];
  });

  const linePath = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p[0]} ${p[1]}`).join(" ");
  const areaPath = `${linePath} L ${points[points.length - 1][0]} ${height} L ${points[0][0]} ${height} Z`;
  const last = points[points.length - 1];
  const gradientId = `spark-${color.replace("#", "")}`;

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full" style={{ height }} preserveAspectRatio="none">
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.28" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill={`url(#${gradientId})`} stroke="none" />
      <path d={linePath} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={last[0]} cy={last[1]} r="2.5" fill={color} />
      <circle cx={last[0]} cy={last[1]} r="5" fill={color} opacity="0.35">
        <animate attributeName="r" values="4;7;4" dur="2s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0.35;0;0.35" dur="2s" repeatCount="indefinite" />
      </circle>
    </svg>
  );
}

const STATUS_COLOR: Record<string, string> = {
  LOW: "#D97B2B",
  OPTIMAL: "#4C7A3F",
  HIGH: "#A32F26",
  UNKNOWN: "#B9B199",
};

/** Horizontal low/optimal/high threshold bar with a marker — reads faster than a
 * speedometer dial and only needs the width of a card, not a whole gauge face. */
export function NutrientBar({
  value,
  lowThreshold,
  highThreshold,
  displayMax,
  status,
}: {
  value: number | null;
  lowThreshold: number;
  highThreshold: number;
  displayMax: number;
  status: string;
}) {
  const color = STATUS_COLOR[status] ?? STATUS_COLOR.UNKNOWN;
  const lowPct = Math.min(100, (lowThreshold / displayMax) * 100);
  const highPct = Math.min(100, (highThreshold / displayMax) * 100);
  const markerPct = value === null ? null : Math.max(2, Math.min(98, (value / displayMax) * 100));

  return (
    <div className="relative pt-3">
      <div className="relative h-2 w-full overflow-hidden rounded-full">
        <div className="absolute inset-y-0 left-0 bg-risk-attention/60" style={{ width: `${lowPct}%` }} />
        <div
          className="absolute inset-y-0 bg-risk-healthy/60"
          style={{ left: `${lowPct}%`, width: `${highPct - lowPct}%` }}
        />
        <div className="absolute inset-y-0 bg-risk-critical/60" style={{ left: `${highPct}%`, right: 0 }} />
      </div>
      {markerPct !== null && (
        <div
          className="absolute top-0 h-4 w-4 -translate-x-1/2 rounded-full border-2 border-white shadow"
          style={{ left: `${markerPct}%`, backgroundColor: color, transition: "left 0.6s ease" }}
        />
      )}
    </div>
  );
}

export function TrendArrow({ trend }: { trend: Trend }) {
  if (trend === "UP") return <span className="text-risk-attention">↑</span>;
  if (trend === "DOWN") return <span className="text-forest">↓</span>;
  return <span className="text-ink/30">→</span>;
}

export { STATUS_COLOR as NUTRIENT_STATUS_COLOR };
