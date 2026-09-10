import { FormEvent, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { USER_IMAGE_02 } from "@/assets/images";
import { HealthBadge } from "@/components/badges";
import { api } from "@/lib/api";
import { useAllFields, useFarms } from "@/lib/queries";
import { useQueryClient } from "@tanstack/react-query";
import { useFieldHealth } from "@/lib/queries";
import type { FieldOut } from "@/types/api";

export default function FieldsPage() {
  const { t } = useTranslation();
  const { data: farms, isLoading: farmsLoading } = useFarms();
  const { data: fields, isLoading: fieldsLoading } = useAllFields(farms);
  const [showNewFarm, setShowNewFarm] = useState(false);

  const loading = farmsLoading || fieldsLoading;

  return (
    <div className="space-y-6">
      <section className="relative overflow-hidden rounded-xl2 shadow-card">
        <img src={USER_IMAGE_02} alt="Sugarcane field beside an intercropped orchard row" className="h-40 w-full object-cover sm:h-48" />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-dark/80 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 p-5">
          <h1 className="text-xl font-bold text-cream sm:text-2xl">{t("fields.heroTitle")}</h1>
          <p className="text-sm text-cream/80">{t("fields.heroSubtitle")}</p>
        </div>
      </section>

      {!farms || farms.length === 0 ? (
        farmsLoading ? (
          <p className="text-ink/60">{t("fields.loadingFarms")}</p>
        ) : (
          <NewFarmCard onCreated={() => setShowNewFarm(false)} />
        )
      ) : (
        <>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-forest">{t("fields.fieldsHeading")}</h2>
            <Link to="/fields/new" className="btn-primary">
              {t("fields.addField")}
            </Link>
          </div>

          {loading && <p className="text-ink/60">{t("fields.loadingFields")}</p>}

          {fields && fields.length === 0 && (
            <div className="card text-center">
              <p className="font-medium text-ink">{t("fields.noScansYet")}</p>
              <p className="mt-1 text-sm text-ink/60">{t("fields.addFieldBoundaryHint")}</p>
              <Link to="/fields/new" className="btn-primary mt-4 inline-flex">
                {t("fields.addFirstField")}
              </Link>
            </div>
          )}

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {fields?.map((f) => (
              <FieldCard key={f.id} field={f} farmName={farms.find((farm) => farm.id === f.farm_id)?.name} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function FieldCard({ field, farmName }: { field: FieldOut; farmName?: string }) {
  const { t } = useTranslation();
  const { data: health } = useFieldHealth(field.id);
  const hectares = field.area_m2 ? (field.area_m2 / 10000).toFixed(2) : null;

  return (
    <Link to={`/fields/${field.id}`} className="card block transition-shadow hover:shadow-lg">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-semibold text-ink">{field.name}</h3>
          <p className="text-sm text-ink/60">
            {field.crop_type ?? t("common.cropNotSet")} {farmName ? `· ${farmName}` : ""}
          </p>
        </div>
        {health && <HealthBadge status={health.status} />}
      </div>
      <div className="mt-3 flex items-center gap-4 text-xs text-ink/50">
        {hectares && (
          <span>
            {hectares} {t("common.hectares")}
          </span>
        )}
        {!field.boundary && <span className="text-soil-dark">{t("common.boundaryNotDrawn")}</span>}
      </div>
      <span className="mt-3 inline-block text-sm font-medium text-forest">{t("common.openField")}</span>
    </Link>
  );
}

function NewFarmCard({ onCreated }: { onCreated: () => void }) {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const qc = useQueryClient();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post("/farms", { name });
      await qc.invalidateQueries({ queryKey: ["farms"] });
      onCreated();
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card max-w-md">
      <h2 className="text-lg font-semibold text-forest">{t("fields.setUpFarm")}</h2>
      <p className="mt-1 text-sm text-ink/60">{t("fields.setUpFarmHint")}</p>
      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <input
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder={t("fields.farmNamePlaceholder")}
          className="input"
        />
        <button type="submit" disabled={loading} className="btn-primary shrink-0">
          {loading ? t("common.creating") : t("fields.create")}
        </button>
      </form>
    </div>
  );
}
