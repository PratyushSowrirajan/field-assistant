import { useTranslation } from "react-i18next";
import type { HealthStatus } from "@/types/api";

const HEALTH_CLASSES: Record<HealthStatus, string> = {
  HEALTHY: "bg-risk-healthy/15 text-risk-healthy",
  MONITOR: "bg-risk-monitor/15 text-risk-monitor",
  ATTENTION: "bg-risk-attention/15 text-risk-attention",
  HIGH_RISK: "bg-risk-high/15 text-risk-high",
  CRITICAL: "bg-risk-critical/15 text-risk-critical",
};

export function HealthBadge({ status }: { status: HealthStatus }) {
  const { t } = useTranslation();
  const className = HEALTH_CLASSES[status] ?? HEALTH_CLASSES.MONITOR;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${className}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {t(`health.${status}`, status)}
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
  const { t } = useTranslation();
  const className = SEVERITY_STYLES[severity] ?? SEVERITY_STYLES.MODERATE;
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${className}`}>
      {t(`status.${severity}`, severity)}
    </span>
  );
}

export function TreatmentBadge({ status }: { status: "TREATED" | "UNTREATED" }) {
  const { t } = useTranslation();
  return status === "TREATED" ? (
    <span className="inline-flex items-center rounded-full bg-leaf/15 px-2.5 py-1 text-xs font-semibold text-leaf-dark">
      {t("common.treated")}
    </span>
  ) : (
    <span className="inline-flex items-center rounded-full bg-soil/15 px-2.5 py-1 text-xs font-semibold text-soil-dark">
      {t("common.notYetTreated")}
    </span>
  );
}
