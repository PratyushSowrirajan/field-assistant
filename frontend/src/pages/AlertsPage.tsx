import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { SeverityBadge } from "@/components/badges";
import { useAcknowledgeAlert, useAlerts } from "@/lib/queries";

export default function AlertsPage() {
  const { t } = useTranslation();
  const STATUS_OPTIONS = [
    { value: "ACTIVE", label: t("alerts.statusActive") },
    { value: "ACKNOWLEDGED", label: t("alerts.statusAcknowledged") },
    { value: "RESOLVED", label: t("alerts.statusResolved") },
  ];
  const [status, setStatus] = useState("ACTIVE");
  const [severity, setSeverity] = useState<string>("");
  const { data: alerts, isLoading } = useAlerts({ status, ...(severity ? { severity } : {}) });
  const acknowledge = useAcknowledgeAlert();

  const statusLabel = STATUS_OPTIONS.find((s) => s.value === status)?.label ?? status;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-bold text-forest">{t("alerts.title")}</h1>
        <div className="flex gap-2">
          <select value={status} onChange={(e) => setStatus(e.target.value)} className="input w-auto">
            {STATUS_OPTIONS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
          <select value={severity} onChange={(e) => setSeverity(e.target.value)} className="input w-auto">
            <option value="">{t("alerts.allSeverities")}</option>
            <option value="CRITICAL">{t("status.CRITICAL")}</option>
            <option value="HIGH">{t("status.HIGH")}</option>
            <option value="MODERATE">{t("status.MODERATE")}</option>
            <option value="LOW">{t("status.LOW")}</option>
          </select>
        </div>
      </div>

      {isLoading && <p className="text-ink/60">{t("common.loading")}</p>}

      {alerts && alerts.length === 0 && (
        <div className="card text-center">
          <p className="text-sm text-ink/60">{t("alerts.noAlerts", { status: statusLabel.toLowerCase() })}</p>
        </div>
      )}

      <ul className="space-y-3">
        {alerts?.map((a) => (
          <li key={a.id} className="card flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <SeverityBadge severity={a.severity} />
                <span className="text-xs text-ink/50">{new Date(a.last_seen_at).toLocaleString()}</span>
              </div>
              <p className="mt-1.5 text-sm text-ink">{a.message}</p>
              <Link to={`/fields/${a.field_id}`} className="mt-1 inline-block text-xs font-medium text-forest hover:underline">
                {a.field_name}
                {a.zone_code ? ` · ${t("common.zone")} ${a.zone_code}` : ""}
              </Link>
            </div>
            {a.status === "ACTIVE" && (
              <button
                onClick={() => acknowledge.mutate(a.id)}
                disabled={acknowledge.isPending}
                className="btn-secondary shrink-0 px-3 py-1.5 text-xs"
              >
                {t("alerts.acknowledge")}
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
