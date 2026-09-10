import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { USER_IMAGE_01 } from "@/assets/images";
import { HealthBadge, SeverityBadge } from "@/components/badges";
import { useAuth } from "@/hooks/useAuth";
import { useDashboard, useRovers } from "@/lib/queries";

function greetingKey() {
  const h = new Date().getHours();
  if (h < 12) return "home.greetingMorning";
  if (h < 17) return "home.greetingAfternoon";
  return "home.greetingEvening";
}

export default function HomePage() {
  const { farmer } = useAuth();
  const { t } = useTranslation();
  const { data: dashboard, isLoading } = useDashboard();
  const { data: rovers } = useRovers();

  const activeRovers = (rovers ?? []).filter((r) => r.status !== "OFFLINE");

  return (
    <div className="space-y-6">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-xl2 shadow-card">
        <img src={USER_IMAGE_01} alt="Farmer with fresh harvest in a mixed crop field" className="h-56 w-full object-cover sm:h-72" />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-dark/85 via-forest-dark/20 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 p-5 sm:p-8">
          <p className="text-sm font-medium text-cream/80">
            {t(greetingKey())}, {farmer?.name?.split(" ")[0] ?? t("home.thereFallback")}.
          </p>
          <h1 className="mt-1 max-w-xl text-2xl font-bold text-cream sm:text-3xl">
            {dashboard && dashboard.fields_requiring_attention > 0
              ? t("home.fieldsNeedAttention", { count: dashboard.fields_requiring_attention })
              : t("home.fieldsLookSteady")}
          </h1>
          <p className="mt-1 text-sm text-cream/80">{t("home.heroSubtitle")}</p>
        </div>
      </section>

      {isLoading && <p className="text-ink/60">{t("common.loading")}</p>}

      {dashboard && (
        <>
          {/* Field overview */}
          <section>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-forest">{t("home.yourFieldsGlance")}</h2>
              <Link to="/fields" className="text-sm font-medium text-forest hover:underline">
                {t("home.viewAllFields")}
              </Link>
            </div>
            {dashboard.fields.length === 0 ? (
              <EmptyFieldsCard />
            ) : (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {dashboard.fields.slice(0, 6).map((f) => (
                  <Link key={f.id} to={`/fields/${f.id}`} className="card block transition-shadow hover:shadow-lg">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="font-semibold text-ink">{f.name}</h3>
                        <p className="text-sm text-ink/60">{f.crop_type ?? t("common.cropNotSet")}</p>
                      </div>
                      <HealthBadge status={f.health_status} />
                    </div>
                    {f.top_issue && <p className="mt-3 text-sm text-ink/80 line-clamp-2">{f.top_issue}</p>}
                    <div className="mt-3 flex items-center justify-between text-xs text-ink/50">
                      <span>
                        {f.last_scan_at
                          ? t("home.lastScan", { time: new Date(f.last_scan_at).toLocaleString() })
                          : t("home.noScansYet")}
                      </span>
                      {f.rover_status && <span className="font-medium text-leaf-dark">{f.rover_status}</span>}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </section>

          {/* Needs attention + live activity */}
          <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div className="card">
              <h2 className="mb-3 text-base font-semibold text-forest">{t("home.needsAttention")}</h2>
              {dashboard.top_alerts.length === 0 ? (
                <p className="text-sm text-ink/60">{t("home.noActiveAlerts")}</p>
              ) : (
                <ul className="space-y-3">
                  {dashboard.top_alerts.map((a) => (
                    <li key={a.id}>
                      <Link
                        to={`/fields/${a.field_id}`}
                        className="flex items-start gap-3 rounded-lg p-2 -m-2 hover:bg-sand/60"
                      >
                        <SeverityBadge severity={a.severity} />
                        <div className="min-w-0">
                          <p className="text-sm text-ink">{a.message}</p>
                          <p className="text-xs text-ink/50">
                            {a.field_name}
                            {a.zone_code ? ` · ${t("common.zone")} ${a.zone_code}` : ""}
                          </p>
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="card">
              <h2 className="mb-3 text-base font-semibold text-forest">{t("home.currentRoverActivity")}</h2>
              {activeRovers.length === 0 ? (
                <p className="text-sm text-ink/60">{t("home.noActiveRover")}</p>
              ) : (
                <ul className="space-y-3">
                  {activeRovers.map((r) => (
                    <li key={r.id}>
                      <Link to="/live" className="flex items-center justify-between rounded-lg p-2 -m-2 hover:bg-sand/60">
                        <div>
                          <p className="text-sm font-medium text-ink">{r.name}</p>
                          <p className="text-xs text-ink/50">{r.status}</p>
                        </div>
                        <span className="h-2.5 w-2.5 rounded-full bg-leaf" />
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function EmptyFieldsCard() {
  const { t } = useTranslation();
  return (
    <div className="card text-center">
      <p className="font-medium text-ink">{t("home.noFieldsYet")}</p>
      <p className="mt-1 text-sm text-ink/60">{t("home.addFirstFieldHint")}</p>
      <Link to="/fields/new" className="btn-primary mt-4 inline-flex">
        {t("home.addAField")}
      </Link>
    </div>
  );
}
