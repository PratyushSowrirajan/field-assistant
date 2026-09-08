export type GeoJSONPolygon = {
  type: "Polygon";
  coordinates: [number, number][][];
};

export type GeoJSONPoint = {
  type: "Point";
  coordinates: [number, number];
};

export type GeoJSONLineString = {
  type: "LineString";
  coordinates: [number, number][];
};

export interface Farmer {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  role: string;
}

export interface Farm {
  id: string;
  name: string;
  archived: boolean;
  created_at: string;
  field_count: number;
}

export interface FieldOut {
  id: string;
  farm_id: string;
  name: string;
  crop_type: string | null;
  crop_variety: string | null;
  planting_date: string | null;
  expected_harvest_date: string | null;
  area_m2: number | null;
  zone_resolution_m: number | null;
  archived: boolean;
  created_at: string;
  boundary: GeoJSONPolygon | null;
}

export interface ZoneOut {
  id: string;
  field_id: string;
  code: string;
  area_m2: number;
  resolution_m: number;
  polygon: GeoJSONPolygon;
}

export interface ZoneSummary {
  id: string;
  code: string;
  area_m2: number;
  disease_prevalence_pct: number;
  pest_prevalence_pct: number;
  nutrient_risk: string;
  risk_level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
  trend: "INCREASING" | "DECREASING" | "STABLE";
  observation_count: number;
  detection_count: number;
  treatment_status: "TREATED" | "UNTREATED";
  last_scan_at: string | null;
}

export type HealthStatus = "HEALTHY" | "MONITOR" | "ATTENTION" | "HIGH_RISK" | "CRITICAL";

export interface FieldHealthOut {
  field_id: string;
  status: HealthStatus;
  score: number;
  disease_prevalence_pct: number;
  pest_prevalence_pct: number;
  water_stress_status: string;
  environmental_risk: string;
  yield_risk: string;
}

export interface RoverOut {
  id: string;
  device_id: string;
  name: string;
  status: string;
  sprayer_status: string | null;
  battery_level: number | null;
  firmware_version: string | null;
  last_seen_at: string | null;
  field_ids: string[];
}

export interface RoverLiveState {
  rover_id: string;
  device_id: string;
  status: string;
  sprayer_status: string | null;
  battery_level: number | null;
  latitude: number | null;
  longitude: number | null;
  speed_mps: number | null;
  heading_deg: number | null;
  field_id: string | null;
  zone_id: string | null;
  zone_code: string | null;
  scan_session_id: string | null;
  latest_detection: { detection_type: string; class_name: string; confidence: number } | null;
  connection_status: "CONNECTED" | "OFFLINE";
  last_update_at: string | null;
}

export interface AlertOut {
  id: string;
  field_id: string;
  zone_id: string | null;
  zone_code: string | null;
  field_name: string | null;
  type: string;
  severity: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
  message: string;
  status: string;
  acknowledged: boolean;
  created_at: string;
  last_seen_at: string;
}

export interface AdvisoryOut {
  id: string;
  field_id: string;
  zone_id: string | null;
  what: string;
  where_label: string;
  severity: string;
  recommended_action: string;
  action_taken: boolean;
  created_at: string;
}

export interface DetectionOut {
  id: string;
  observation_id: string;
  detection_type: string;
  class_name: string;
  confidence: number;
  severity: string | null;
  model_name: string | null;
  model_version: string | null;
  created_at: string;
  image_uri: string | null;
  latitude: number;
  longitude: number;
  field_id: string | null;
  zone_id: string | null;
  zone_code: string | null;
  rover_id: string;
  scan_session_id: string | null;
  treatment_status: "TREATED" | "UNTREATED";
}

export interface HotspotOut {
  id: string;
  field_id: string;
  zone_id: string | null;
  detection_type: string;
  class_name: string | null;
  center_lat: number;
  center_lon: number;
  detection_count: number;
  density_per_ha: number;
  severity: string;
}

export interface DashboardFieldCard {
  id: string;
  name: string;
  crop_type: string | null;
  area_m2: number | null;
  health_status: HealthStatus;
  top_issue: string | null;
  last_scan_at: string | null;
  rover_status: string | null;
}

export interface DashboardSummary {
  total_fields: number;
  fields_requiring_attention: number;
  active_alerts: number;
  disease_pest_alerts: number;
  water_stress_alerts: number;
  environmental_alerts: number;
  fields: DashboardFieldCard[];
  top_alerts: AlertOut[];
  active_rover_count: number;
}

export interface IrrigationRecommendationOut {
  field_id: string;
  zone_id: string | null;
  recommendation: "IRRIGATE_NOW" | "IRRIGATE_SOON" | "DELAY" | "NO_IRRIGATION" | "UNKNOWN";
  water_stress_status: string;
  over_irrigation_status: string;
  soil_moisture_pct: number | null;
  temperature_c: number | null;
  humidity_pct: number | null;
  forecast_rainfall_mm: number | null;
  reason: string;
}

export interface EnvironmentalRiskOut {
  field_id: string;
  drought_risk: string;
  flood_risk: string;
  heat_risk: string;
  disease_environment_risk: string;
}

export interface YieldRiskOut {
  field_id: string;
  yield_risk: string;
  contributing_factors: string[];
}

export interface TreatmentCoverageOut {
  field_id: string;
  qualifying_detections: number;
  treated_detections: number;
  treatment_coverage_pct: number;
  untreated_problem_count: number;
}

export interface DecisionInsightOut {
  type: string;
  severity: string;
  field_id: string;
  zone_id: string | null;
  message: string;
  evidence: string;
  recommended_action: string;
}

export interface TimeSeriesPoint {
  timestamp: string;
  value: number;
}

export interface RoverRegisterResponse {
  id: string;
  device_id: string;
  device_secret: string;
}
