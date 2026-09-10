import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
  AdvisoryOut,
  AlertOut,
  AssistantAskResponse,
  ChatTurn,
  DashboardSummary,
  DecisionInsightOut,
  DetectionOut,
  EnvironmentalRiskOut,
  Farm,
  FieldHealthOut,
  FieldOut,
  FieldOverviewOut,
  HotspotOut,
  IrrigationRecommendationOut,
  RoverLiveState,
  RoverOut,
  TimeSeriesPoint,
  TreatmentCoverageOut,
  YieldRiskOut,
  ZoneOut,
  ZoneSummary,
} from "@/types/api";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => (await api.get<DashboardSummary>("/dashboard")).data,
    refetchInterval: 30_000,
  });
}

export function useFarms() {
  return useQuery({
    queryKey: ["farms"],
    queryFn: async () => (await api.get<Farm[]>("/farms")).data,
  });
}

export function useFields(farmId?: string) {
  return useQuery({
    queryKey: ["fields", farmId],
    queryFn: async () => (await api.get<FieldOut[]>(`/farms/${farmId}/fields`)).data,
    enabled: !!farmId,
  });
}

export function useAllFields(farms: Farm[] | undefined) {
  return useQuery({
    queryKey: ["all-fields", farms?.map((f) => f.id)],
    queryFn: async () => {
      const results = await Promise.all(
        (farms ?? []).map((f) => api.get<FieldOut[]>(`/farms/${f.id}/fields`))
      );
      return results.flatMap((r) => r.data);
    },
    enabled: !!farms,
  });
}

export function useField(fieldId?: string) {
  return useQuery({
    queryKey: ["field", fieldId],
    queryFn: async () => (await api.get<FieldOut>(`/fields/${fieldId}`)).data,
    enabled: !!fieldId,
  });
}

export function useZones(fieldId?: string) {
  return useQuery({
    queryKey: ["zones", fieldId],
    queryFn: async () => (await api.get<ZoneOut[]>(`/fields/${fieldId}/zones`)).data,
    enabled: !!fieldId,
  });
}

export function useFieldHealth(fieldId?: string) {
  return useQuery({
    queryKey: ["field-health", fieldId],
    queryFn: async () => (await api.get<FieldHealthOut>(`/fields/${fieldId}/health`)).data,
    enabled: !!fieldId,
    refetchInterval: 30_000,
  });
}

export function useFieldOverview(fieldId?: string) {
  return useQuery({
    queryKey: ["field-overview", fieldId],
    queryFn: async () => (await api.get<FieldOverviewOut>(`/fields/${fieldId}/overview`)).data,
    enabled: !!fieldId,
    refetchInterval: 15_000,
  });
}

export function useHotspots(fieldId?: string) {
  return useQuery({
    queryKey: ["hotspots", fieldId],
    queryFn: async () => (await api.get<HotspotOut[]>(`/fields/${fieldId}/hotspots`)).data,
    enabled: !!fieldId,
  });
}

export function useDetections(fieldId?: string, params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ["detections", fieldId, params],
    queryFn: async () =>
      (await api.get<DetectionOut[]>(`/fields/${fieldId}/detections`, { params })).data,
    enabled: !!fieldId,
  });
}

export function useIrrigation(fieldId?: string) {
  return useQuery({
    queryKey: ["irrigation", fieldId],
    queryFn: async () => (await api.get<IrrigationRecommendationOut>(`/fields/${fieldId}/irrigation`)).data,
    enabled: !!fieldId,
  });
}

export function useEnvironmentalRisk(fieldId?: string) {
  return useQuery({
    queryKey: ["env-risk", fieldId],
    queryFn: async () => (await api.get<EnvironmentalRiskOut>(`/fields/${fieldId}/environmental-risk`)).data,
    enabled: !!fieldId,
  });
}

export function useYieldRisk(fieldId?: string) {
  return useQuery({
    queryKey: ["yield-risk", fieldId],
    queryFn: async () => (await api.get<YieldRiskOut>(`/fields/${fieldId}/yield-risk`)).data,
    enabled: !!fieldId,
  });
}

export function useTreatmentCoverage(fieldId?: string) {
  return useQuery({
    queryKey: ["treatment-coverage", fieldId],
    queryFn: async () => (await api.get<TreatmentCoverageOut>(`/fields/${fieldId}/treatment-coverage`)).data,
    enabled: !!fieldId,
  });
}

export function useInsights(fieldId?: string) {
  return useQuery({
    queryKey: ["insights", fieldId],
    queryFn: async () => (await api.get<DecisionInsightOut[]>(`/fields/${fieldId}/insights`)).data,
    enabled: !!fieldId,
  });
}

export function useTimeSeries(fieldId: string | undefined, metric: string, days = 30) {
  return useQuery({
    queryKey: ["timeseries", fieldId, metric, days],
    queryFn: async () =>
      (await api.get<TimeSeriesPoint[]>(`/fields/${fieldId}/timeseries`, { params: { metric, days } })).data,
    enabled: !!fieldId,
  });
}

export function useZoneSummary(zoneId?: string) {
  return useQuery({
    queryKey: ["zone-summary", zoneId],
    queryFn: async () => (await api.get<ZoneSummary>(`/zones/${zoneId}/summary`)).data,
    enabled: !!zoneId,
  });
}

export function useAlerts(params: Record<string, string> = {}) {
  return useQuery({
    queryKey: ["alerts", params],
    queryFn: async () => (await api.get<AlertOut[]>("/alerts", { params })).data,
    refetchInterval: 30_000,
  });
}

export function useAdvisories(fieldId?: string) {
  return useQuery({
    queryKey: ["advisories", fieldId],
    queryFn: async () =>
      (await api.get<AdvisoryOut[]>("/advisories", { params: fieldId ? { field_id: fieldId } : {} })).data,
  });
}

export function useAcknowledgeAlert() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (alertId: string) => (await api.post(`/alerts/${alertId}/acknowledge`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["alerts"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useRovers() {
  return useQuery({
    queryKey: ["rovers"],
    queryFn: async () => (await api.get<RoverOut[]>("/rovers")).data,
    refetchInterval: 20_000,
  });
}

export function useRoverLive(roverId?: string) {
  return useQuery({
    queryKey: ["rover-live", roverId],
    queryFn: async () => (await api.get<RoverLiveState>(`/rovers/${roverId}/live`)).data,
    enabled: !!roverId,
    refetchInterval: 10_000,
  });
}

export function useGenerateSprayRecommendations(fieldId?: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => (await api.post(`/fields/${fieldId}/spray-recommendations/generate`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["spray-recommendations", fieldId] }),
  });
}

export function useRefreshWeather(fieldId?: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => (await api.post(`/fields/${fieldId}/weather/refresh`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["irrigation", fieldId] });
      qc.invalidateQueries({ queryKey: ["env-risk", fieldId] });
      qc.invalidateQueries({ queryKey: ["field-health", fieldId] });
    },
  });
}

export function useAskAssistant() {
  return useMutation({
    mutationFn: async (vars: { question: string; fieldId?: string; history: ChatTurn[] }) =>
      (
        await api.post<AssistantAskResponse>("/assistant/ask", {
          question: vars.question,
          field_id: vars.fieldId,
          history: vars.history,
        })
      ).data,
  });
}
