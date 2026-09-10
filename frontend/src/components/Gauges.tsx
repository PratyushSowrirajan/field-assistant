import type { Trend } from "@/types/api";

const RISK_COLORS: Record<string, string> = {
  HEALTHY: "#4C7A3F", // leaf
  MONITOR: "#C89B2E",
  ATTENTION: "#D97B2B",
  HIGH_RISK: "#C1502E",
  CRITICAL: "#A32F26",
};

function polarPoint(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = (angleDeg * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy - r * Math.sin(rad) };
}

function arcPath(cx: number, cy: number, r: number, startDeg: number, endDeg: number) {
  const start = polarPoint(cx, cy, r, startDeg);
  const end = polarPoint(cx, cy, r, endDeg);
  const largeArc = Math.abs(startDeg - endDeg) > 180 ? 1 : 0;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y}`;
}

/** Circular "health score" ring, e.g. the 78/100 dial on the field header. */
export function HealthRing({ score, status }: { score: number; status: string }) {
  const clamped = Math.max(0, Math.min(100, score));
  const color = RISK_COLORS[status] ?? RISK_COLORS.MONITOR;
  const r = 42;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - clamped / 100);

  return (
    <div className="relative h-28 w-28 shrink-0">
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
          style={{ transition: "stroke-dashoffset 0.6s ease" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-ink">{Math.round(clamped)}</span>
        <span className="text-[10px] font-medium uppercase tracking-wide text-ink/50">Health</span>
      </div>
    </div>
  );
}

const NUTRIENT_ZONE_COLORS = ["#D97B2B", "#4C7A3F", "#C1502E"]; // low, optimal, high

/** Semi-circle "speedometer" gauge for a nutrient reading, with a low/optimal/high band. */
export function NutrientGauge({
  value,
  displayMax,
  unit,
}: {
  value: number | null;
  displayMax: number;
  unit: string;
}) {
  const cx = 60;
  const cy = 58;
  const r = 46;
  const fraction = value === null ? 0 : Math.max(0, Math.min(1, value / displayMax));
  const needleAngle = 180 - fraction * 180;
  const needleTip = polarPoint(cx, cy, r - 10, needleAngle);

  const bands = [
    { start: 180, end: 120 },
    { start: 120, end: 60 },
    { start: 60, end: 0 },
  ];

  return (
    <svg viewBox="0 0 120 68" className="h-24 w-full">
      {bands.map((b, i) => (
        <path
          key={i}
          d={arcPath(cx, cy, r, b.start, b.end)}
          fill="none"
          stroke={NUTRIENT_ZONE_COLORS[i]}
          strokeWidth="9"
          strokeLinecap="butt"
          opacity={value === null ? 0.25 : 0.85}
        />
      ))}
      {value !== null && (
        <line
          x1={cx}
          y1={cy}
          x2={needleTip.x}
          y2={needleTip.y}
          stroke="#26291F"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
      )}
      <circle cx={cx} cy={cy} r="3.5" fill="#26291F" />
      <text x={cx} y={cy - 14} textAnchor="middle" className="fill-ink text-[13px] font-bold">
        {value === null ? "—" : `${value.toFixed(0)}${unit}`}
      </text>
    </svg>
  );
}

export function TrendArrow({ trend }: { trend: Trend }) {
  if (trend === "UP") return <span className="text-risk-attention">↑</span>;
  if (trend === "DOWN") return <span className="text-forest">↓</span>;
  return <span className="text-ink/30">→</span>;
}
