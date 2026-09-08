import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { useEffect, useRef } from "react";
import { MAPBOX_TOKEN } from "@/lib/api";

mapboxgl.accessToken = MAPBOX_TOKEN;

const DEFAULT_CENTER: [number, number] = [80.2707, 13.0827]; // Chennai region — sensible default for an India-focused deployment

interface Props {
  points: [number, number][]; // [lon, lat]
  onAddPoint: (point: [number, number]) => void;
}

export default function FieldBoundaryMap({ points, onAddPoint }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const pointsRef = useRef(points);
  pointsRef.current = points;

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/satellite-streets-v12",
      center: DEFAULT_CENTER,
      zoom: 16,
    });
    mapRef.current = map;
    map.addControl(new mapboxgl.NavigationControl(), "top-right");

    map.on("load", () => {
      map.addSource("draft-boundary", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
      });
      map.addLayer({
        id: "draft-fill",
        type: "fill",
        source: "draft-boundary",
        filter: ["==", "$type", "Polygon"],
        paint: { "fill-color": "#4C7A3F", "fill-opacity": 0.25 },
      });
      map.addLayer({
        id: "draft-line",
        type: "line",
        source: "draft-boundary",
        paint: { "line-color": "#1F3D2B", "line-width": 2.5 },
      });
      map.addLayer({
        id: "draft-points",
        type: "circle",
        source: "draft-boundary",
        filter: ["==", "$type", "Point"],
        paint: { "circle-color": "#1F3D2B", "circle-radius": 5, "circle-stroke-color": "#fff", "circle-stroke-width": 2 },
      });
      renderPoints(map, pointsRef.current);
    });

    map.on("click", (e) => {
      onAddPoint([e.lngLat.lng, e.lngLat.lat]);
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    if (map.isStyleLoaded()) renderPoints(map, points);
  }, [points]);

  return <div ref={containerRef} className="h-full w-full rounded-xl2" />;
}

function renderPoints(map: mapboxgl.Map, points: [number, number][]) {
  const source = map.getSource("draft-boundary") as mapboxgl.GeoJSONSource | undefined;
  if (!source) return;

  const features: GeoJSON.Feature[] = points.map((p) => ({
    type: "Feature",
    geometry: { type: "Point", coordinates: p },
    properties: {},
  }));

  if (points.length >= 2) {
    const ring = points.length >= 3 ? [...points, points[0]] : points;
    features.push({
      type: "Feature",
      geometry: points.length >= 3 ? { type: "Polygon", coordinates: [ring] } : { type: "LineString", coordinates: ring },
      properties: {},
    });
  }

  source.setData({ type: "FeatureCollection", features });
}
