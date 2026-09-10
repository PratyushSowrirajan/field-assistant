import { FormEvent, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { USER_IMAGE_03 } from "@/assets/images";
import FieldMap from "@/components/FieldMap";
import { api } from "@/lib/api";
import { useField, useRoverLive, useRovers, useZones } from "@/lib/queries";
import { useLiveFeed } from "@/hooks/useLiveFeed";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { RoverLiveState } from "@/types/api";

export default function LiveRoverPage() {
  const { t } = useTranslation();
  const { data: rovers, isLoading } = useRovers();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    if (!selectedId && rovers && rovers.length > 0) setSelectedId(rovers[0].id);
  }, [rovers, selectedId]);

  const selected = rovers?.find((r) => r.id === selectedId);

  return (
    <div className="space-y-5">
      <section className="relative overflow-hidden rounded-xl2 shadow-card">
        <img src={USER_IMAGE_03} alt="Farmers preparing natural inputs beside the field" className="h-36 w-full object-cover sm:h-44" />
        <div className="absolute inset-0 bg-gradient-to-t from-forest-dark/80 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 p-5">
          <h1 className="text-xl font-bold text-cream sm:text-2xl">{t("liveRover.heroTitle")}</h1>
          <p className="text-sm text-cream/80">{t("liveRover.heroSubtitle")}</p>
        </div>
      </section>

      {isLoading && <p className="text-ink/60">{t("liveRover.loadingRovers")}</p>}

      {rovers && rovers.length === 0 && !showRegister && (
        <div className="card text-center">
          <p className="font-medium text-ink">{t("liveRover.noRoverPaired")}</p>
          <p className="mt-1 text-sm text-ink/60">{t("liveRover.registerRoverHint")}</p>
          <button onClick={() => setShowRegister(true)} className="btn-primary mt-4 inline-flex">
            {t("liveRover.registerRover")}
          </button>
        </div>
      )}

      {showRegister && <RegisterRoverCard onDone={() => setShowRegister(false)} />}

      {rovers && rovers.length > 0 && (
        <>
          <div className="flex flex-wrap items-center gap-2">
            {rovers.map((r) => (
              <button
                key={r.id}
                onClick={() => setSelectedId(r.id)}
                className={`rounded-full px-4 py-1.5 text-sm font-medium ${
                  selectedId === r.id ? "bg-forest text-cream" : "border border-sand text-ink/70 hover:bg-sand"
                }`}
              >
                {r.name}
              </button>
            ))}
            <button onClick={() => setShowRegister((v) => !v)} className="btn-secondary px-3 py-1.5 text-xs">
              {t("liveRover.addRover")}
            </button>
          </div>

          {selected && <RoverPanel roverId={selected.id} roverName={selected.name} />}
        </>
      )}
    </div>
  );
}

function RoverPanel({ roverId, roverName }: { roverId: string; roverName: string }) {
  const { t } = useTranslation();
  const { data: initial } = useRoverLive(roverId);
  const { lastMessage, connected } = useLiveFeed();
  const qc = useQueryClient();

  const live: RoverLiveState | undefined =
    lastMessage?.rover_id === roverId ? { ...initial, ...lastMessage } : initial;

  useEffect(() => {
    if (lastMessage?.rover_id === roverId) {
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    }
  }, [lastMessage, roverId, qc]);

  const { data: field } = useField(live?.field_id ?? undefined);
  const { data: zones = [] } = useZones(live?.field_id ?? undefined);

  const { data: route } = useQuery({
    queryKey: ["rover-route", roverId, live?.scan_session_id],
    queryFn: async () =>
      (await api.get(`/rovers/${roverId}/route`, { params: live?.scan_session_id ? { scan_session_id: live.scan_session_id } : {} })).data,
    enabled: !!roverId,
    refetchInterval: 15_000,
  });

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_320px]">
      <div className="h-[360px] overflow-hidden rounded-xl2 border border-sand shadow-card sm:h-[460px]">
        {field?.boundary ? (
          <FieldMap
            field={field}
            zones={zones}
            roverLive={live}
            roverRoute={route?.route}
            className="h-full w-full"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-ink/50">
            {live?.field_id ? t("liveRover.preparingMap") : t("liveRover.noMappedPosition")}
          </div>
        )}
      </div>

      <div className="space-y-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-ink">{roverName}</h2>
            <span
              className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${
                connected && live?.connection_status === "CONNECTED"
                  ? "bg-leaf/15 text-leaf-dark"
                  : "bg-soil/15 text-soil-dark"
              }`}
            >
              <span className="h-1.5 w-1.5 rounded-full bg-current" />
              {connected && live?.connection_status === "CONNECTED" ? t("liveRover.connected") : t("liveRover.offline")}
            </span>
          </div>
          <p className="mt-1 text-sm font-medium text-forest">{live?.status ?? t("liveRover.unknown")}</p>
          {live?.zone_code && (
            <p className="text-sm text-ink/60">
              {t("common.zone")} {live.zone_code}
            </p>
          )}
          <p className="mt-2 text-xs text-ink/50">
            {live?.last_update_at
              ? t("liveRover.lastUpdate", { time: new Date(live.last_update_at).toLocaleTimeString() })
              : t("liveRover.noUpdatesYet")}
          </p>
        </div>

        {live?.latest_detection && (
          <div className="card">
            <h3 className="text-sm font-semibold text-forest">{t("liveRover.latestObservation")}</h3>
            <p className="mt-1 text-sm text-ink">
              {live.latest_detection.class_name.replace(/_/g, " ")} · {(live.latest_detection.confidence * 100).toFixed(0)}%
            </p>
          </div>
        )}

        <div className="card space-y-2 text-sm">
          <Row label={t("liveRover.battery")} value={live?.battery_level != null ? `${live.battery_level}%` : "—"} />
          <Row label={t("liveRover.speed")} value={live?.speed_mps != null ? `${live.speed_mps.toFixed(1)} m/s` : "—"} />
          <Row label={t("liveRover.heading")} value={live?.heading_deg != null ? `${live.heading_deg}°` : "—"} />
          <Row label={t("liveRover.sprayer")} value={live?.sprayer_status ?? "—"} />
        </div>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-ink/50">{label}</span>
      <span className="font-medium text-ink">{value}</span>
    </div>
  );
}

function RegisterRoverCard({ onDone }: { onDone: () => void }) {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [deviceId, setDeviceId] = useState("");
  const [secret, setSecret] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const qc = useQueryClient();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await api.post("/rovers", { name, device_id: deviceId, field_ids: [] });
      setSecret(res.data.device_secret);
      await qc.invalidateQueries({ queryKey: ["rovers"] });
    } finally {
      setSubmitting(false);
    }
  }

  if (secret) {
    return (
      <div className="card max-w-lg">
        <h3 className="font-semibold text-forest">{t("liveRover.roverRegistered")}</h3>
        <p className="mt-1 text-sm text-ink/70">{t("liveRover.saveSecretHint")}</p>
        <code className="mt-3 block break-all rounded-lg bg-sand p-3 text-xs">{secret}</code>
        <button onClick={onDone} className="btn-primary mt-4">
          {t("common.done")}
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="card max-w-lg space-y-3">
      <h3 className="font-semibold text-forest">{t("liveRover.registerRover")}</h3>
      <label className="block">
        <span className="mb-1 block text-sm font-medium text-ink/80">{t("liveRover.roverName")}</span>
        <input required value={name} onChange={(e) => setName(e.target.value)} className="input" placeholder={t("liveRover.roverNamePlaceholder")} />
      </label>
      <label className="block">
        <span className="mb-1 block text-sm font-medium text-ink/80">{t("liveRover.deviceId")}</span>
        <input required value={deviceId} onChange={(e) => setDeviceId(e.target.value)} className="input" placeholder={t("liveRover.deviceIdPlaceholder")} />
      </label>
      <p className="text-xs text-ink/50">{t("liveRover.assignFieldsHint")}</p>
      <button type="submit" disabled={submitting} className="btn-primary">
        {submitting ? t("liveRover.registering") : t("liveRover.registerRover")}
      </button>
    </form>
  );
}
