import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { useEffect, useRef, useState } from "react";
import { MAPBOX_TOKEN } from "@/lib/api";
import type { DetectionOut, FieldOut, GeoJSONLineString, HotspotOut, RoverLiveState, ZoneOut } from "@/types/api";

mapboxgl.accessToken = MAPBOX_TOKEN;

const DETECTION_COLORS: Record<string, string> = {
  DISEASE: "#C1502E",
  PEST: "#C89B2E",
  NUTRIENT_DEFICIENCY: "#7A7550",
};

const SEVERITY_FILL: Record<string, string> = {
  LOW: "#4C7A3F",
  MODERATE: "#C89B2E",
  HIGH: "#D97B2B",
  CRITICAL: "#A32F26",
};

interface Props {
  field: FieldOut;
  zones: ZoneOut[];
  hotspots?: HotspotOut[];
  detections?: DetectionOut[];
  roverLive?: RoverLiveState | null;
  roverRoute?: GeoJSONLineString | null;
  onZoneClick?: (zoneId: string) => void;
  onDetectionClick?: (detectionId: string) => void;
  className?: string;
}

const LAYER_OPTIONS = [
  { id: "detections", label: "Detections", defaultOn: true },
  { id: "hotspots", label: "Hotspots", defaultOn: true },
  { id: "route", label: "Rover route", defaultOn: false },
  { id: "treatment", label: "Treated areas", defaultOn: false },
];

export default function FieldMap({
  field,
  zones,
  hotspots = [],
  detections = [],
  roverLive,
  roverRoute,
  onZoneClick,
  onDetectionClick,
  className,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const roverMarkerRef = useRef<mapboxgl.Marker | null>(null);
  const [ready, setReady] = useState(false);
  const [layers, setLayers] = useState<Record<string, boolean>>(
    Object.fromEntries(LAYER_OPTIONS.map((l) => [l.id, l.defaultOn]))
  );

  useEffect(() => {
    if (!containerRef.current || mapRef.current || !field.boundary) return;

    const coords = field.boundary.coordinates[0];
    const lons = coords.map((c) => c[0]);
    const lats = coords.map((c) => c[1]);
    const bounds: [[number, number], [number, number]] = [
      [Math.min(...lons), Math.min(...lats)],
      [Math.max(...lons), Math.max(...lats)],
    ];

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/satellite-streets-v12",
      bounds,
      fitBoundsOptions: { padding: 40 },
    });
    mapRef.current = map;
    map.addControl(new mapboxgl.NavigationControl(), "top-right");

    map.on("load", () => {
      map.addSource("field-boundary", {
        type: "geojson",
        data: { type: "Feature", geometry: field.boundary!, properties: {} },
      });
      map.addLayer({
        id: "field-boundary-line",
        type: "line",
        source: "field-boundary",
        paint: { "line-color": "#1F3D2B", "line-width": 3 },
      });

      map.addSource("zones", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      map.addLayer({
        id: "zones-fill",
        type: "fill",
        source: "zones",
        paint: { "fill-color": ["get", "fillColor"], "fill-opacity": 0.35 },
      });
      map.addLayer({
        id: "zones-line",
        type: "line",
        source: "zones",
        paint: { "line-color": "#F1E9D8", "line-width": 1 },
      });
      map.addLayer({
        id: "zones-label",
        type: "symbol",
        source: "zones",
        layout: { "text-field": ["get", "code"], "text-size": 11 },
        paint: { "text-color": "#26291F", "text-halo-color": "#FBF7EE", "text-halo-width": 1 },
      });
      map.on("click", "zones-fill", (e) => {
        const id = e.features?.[0]?.properties?.zoneId;
        if (id) onZoneClick?.(id);
      });
      map.on("mouseenter", "zones-fill", () => (map.getCanvas().style.cursor = "pointer"));
      map.on("mouseleave", "zones-fill", () => (map.getCanvas().style.cursor = ""));

      map.addSource("hotspots", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      map.addLayer({
        id: "hotspots-circle",
        type: "circle",
        source: "hotspots",
        paint: {
          "circle-radius": ["interpolate", ["linear"], ["get", "count"], 2, 10, 20, 26],
          "circle-color": ["get", "color"],
          "circle-opacity": 0.35,
          "circle-stroke-color": ["get", "color"],
          "circle-stroke-width": 1.5,
        },
      });

      map.addSource("detections", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      map.addLayer({
        id: "detections-circle",
        type: "circle",
        source: "detections",
        paint: {
          "circle-radius": 6,
          "circle-color": ["get", "color"],
          "circle-stroke-color": "#fff",
          "circle-stroke-width": ["case", ["get", "treated"], 0, 1.5],
          "circle-opacity": ["case", ["get", "treated"], 0.45, 1],
        },
      });
      map.on("click", "detections-circle", (e) => {
        const id = e.features?.[0]?.properties?.id;
        if (id) onDetectionClick?.(id);
      });
      map.on("mouseenter", "detections-circle", () => (map.getCanvas().style.cursor = "pointer"));
      map.on("mouseleave", "detections-circle", () => (map.getCanvas().style.cursor = ""));

      map.addSource("route", { type: "geojson", data: { type: "Feature", geometry: { type: "LineString", coordinates: [] }, properties: {} } });
      map.addLayer({
        id: "route-line",
        type: "line",
        source: "route",
        paint: { "line-color": "#2B5039", "line-width": 3, "line-dasharray": [1, 1.5] },
      });

      setReady(true);
    });

    return () => {
      map.remove();
      mapRef.current = null;
      setReady(false);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [field.id]);

  // zones + hotspot tint
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;
    const src = map.getSource("zones") as mapboxgl.GeoJSONSource;
    const hotspotByZone = new Map(hotspots.map((h) => [h.zone_id, h]));
    src?.setData({
      type: "FeatureCollection",
      features: zones.map((z) => {
        const hs = hotspotByZone.get(z.id);
        return {
          type: "Feature",
          geometry: z.polygon,
          properties: {
            zoneId: z.id,
            code: z.code,
            fillColor: hs ? SEVERITY_FILL[hs.severity] ?? "#8A5A3B" : "#4C7A3F",
          },
        };
      }),
    });
  }, [zones, hotspots, ready]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;
    const src = map.getSource("hotspots") as mapboxgl.GeoJSONSource;
    src?.setData({
      type: "FeatureCollection",
      features: layers.hotspots
        ? hotspots.map((h) => ({
            type: "Feature",
            geometry: { type: "Point", coordinates: [h.center_lon, h.center_lat] },
            properties: { count: h.detection_count, color: SEVERITY_FILL[h.severity] ?? "#8A5A3B" },
          }))
        : [],
    });
  }, [hotspots, layers.hotspots, ready]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;
    const src = map.getSource("detections") as mapboxgl.GeoJSONSource;
    src?.setData({
      type: "FeatureCollection",
      features: layers.detections
        ? detections.map((d) => ({
            type: "Feature",
            geometry: { type: "Point", coordinates: [d.longitude, d.latitude] },
            properties: {
              id: d.id,
              color: DETECTION_COLORS[d.detection_type] ?? "#7A7550",
              treated: layers.treatment && d.treatment_status === "TREATED",
            },
          }))
        : [],
    });
  }, [detections, layers.detections, layers.treatment, ready]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;
    const src = map.getSource("route") as mapboxgl.GeoJSONSource;
    src?.setData({
      type: "Feature",
      geometry: layers.route && roverRoute ? roverRoute : { type: "LineString", coordinates: [] },
      properties: {},
    });
  }, [roverRoute, layers.route, ready]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;

    if (!roverLive?.latitude || !roverLive?.longitude) {
      roverMarkerRef.current?.remove();
      roverMarkerRef.current = null;
      return;
    }

    if (!roverMarkerRef.current) {
      const el = document.createElement("div");
      el.className = "rover-marker";
      el.innerHTML = `<div style="width:18px;height:18px;border-radius:9999px;background:#1F3D2B;border:3px solid #FBF7EE;box-shadow:0 0 0 4px rgba(31,61,43,0.25)"></div>`;
      roverMarkerRef.current = new mapboxgl.Marker({ element: el });
    }
    roverMarkerRef.current.setLngLat([roverLive.longitude, roverLive.latitude]).addTo(map);
  }, [roverLive, ready]);

  return (
    <div className={`relative ${className ?? ""}`}>
      <div ref={containerRef} className="h-full w-full rounded-xl2" />
      <div className="absolute right-3 top-3 z-10 rounded-lg border border-sand bg-white/95 p-2 text-xs shadow-card sm:right-16">
        {LAYER_OPTIONS.map((opt) => (
          <label key={opt.id} className="flex items-center gap-2 px-1.5 py-1">
            <input
              type="checkbox"
              checked={layers[opt.id]}
              onChange={(e) => setLayers((prev) => ({ ...prev, [opt.id]: e.target.checked }))}
              className="accent-forest"
            />
            {opt.label}
          </label>
        ))}
      </div>
    </div>
  );
}
