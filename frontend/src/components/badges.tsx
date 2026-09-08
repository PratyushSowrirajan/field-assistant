import type { HealthStatus } from "@/types/api";

const HEALTH_STYLES: Record<HealthStatus, { label: string; className: string }> = {
  HEALTHY: { label: "Healthy", className: "bg-risk-healthy/15 text-risk-healthy" },
  MONITOR: { label: "Monitor", className: "bg-risk-monitor/15 text-risk-monitor" },
  ATTENTION: { label: "Attention required", className: "bg-risk-attention/15 text-risk-attention" },
  HIGH_RISK: { label: "High risk", className: "bg-risk-high/15 text-risk-high" },
  CRITICAL: { label: "Critical", className: "bg-risk-critical/15 text-risk-critical" },
};

export function HealthBadge({ status }: { status: HealthStatus }) {
  const s = HEALTH_STYLES[status] ?? HEALTH_STYLES.MONITOR;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${s.className}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {s.label}
    </span>
  );
}

const SEVERITY_STYLES: Record<string, string> = {
  LOW: "bg-risk-healthy/15 text-risk-healthy",
  MODERATE: "bg-risk-monitor/15 text-risk-monitor",
  HIGH: "bg-risk-attention/15 text-risk-attention",
  CRITICAL: "bg-risk-critical/15 text-risk-critical",
};

export function SeverityBadge({ severity }: { severity: string }) {
  const className = SEVERITY_STYLES[severity] ?? SEVERITY_STYLES.MODERATE;
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${className}`}>
      {severity}
    </span>
  );
}

export function TreatmentBadge({ status }: { status: "TREATED" | "UNTREATED" }) {
  return status === "TREATED" ? (
    <span className="inline-flex items-center rounded-full bg-leaf/15 px-2.5 py-1 text-xs font-semibold text-leaf-dark">
      Treated
    </span>
  ) : (
    <span className="inline-flex items-center rounded-full bg-soil/15 px-2.5 py-1 text-xs font-semibold text-soil-dark">
      Not yet treated
    </span>
  );
}
