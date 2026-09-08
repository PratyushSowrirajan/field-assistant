# PRD — AI Smart Farming Assistant
## Software Application — Initial Version (v2)

**Problem Statement ID:** 26180  
**Organization:** Qualcomm Inc.  
**Product scope:** Backend + Web/Mobile Farmer Dashboard + Edge/Rover Integration Layer  
**Status:** Initial software PRD — subject to revision before implementation

---

# 1. Product Objective

Build a software platform that converts real-time edge/rover observations into actionable, location-aware farm intelligence.

The software must support the requirements in the supplied problem statement:

- Crop disease detection.
- Nutrient-deficiency identification.
- Crop growth-stage and overall field-health monitoring.
- Pest detection and infestation-pattern analysis.
- Early warnings.
- Targeted intervention instead of blanket pesticide application.
- Soil-moisture, temperature, humidity, and weather monitoring.
- Water-stress and over-irrigation detection.
- Irrigation recommendations.
- Drought, excessive-rainfall, flood, heat-stress, and disease-outbreak risk monitoring.
- Edge/on-device processing and low-latency operation.
- Offline/intermittent-connectivity operation.
- Farmer advisories and alerts.
- Historical farm analytics.
- Field-level performance monitoring.
- Yield-risk forecasting and decision-support insights.
- Integration with farm equipment and irrigation systems.
- Scalability from smallholder farms to cooperatives and larger agricultural operations.

The supplied problem statement explicitly requires real-time monitoring, actionable recommendations, field-level alerts, historical analytics, and edge operation in areas with poor connectivity.  
<span style="color:gray">Source: Qualcomm problem statement → application requirements.</span>

---

# 2. Software / Hardware Responsibility Boundary

The application is a software system. Hardware is an upstream data producer and actuator.

## Hardware / Edge side

Expected to provide:

- AMB82-MINI camera/image or video capture.
- CNN inference on the selected edge device.
- Rover movement/telemetry.
- GPS/GNSS position.
- Soil/environmental sensor readings where hardware is installed.
- Sprayer state/control telemetry.
- Irrigation-equipment telemetry where integrated.
- Raspberry Pi as the local integration/controller between hardware and software.

<span style="color:gray">Rover-populated data: from Raspberry Pi / AMB82-MINI / GPS / sensors / rover controller → JSON events required by the backend.</span>

## Software side

The application shall:

- Receive and validate edge data.
- Store raw observations.
- Map observations to fields and zones.
- Calculate derived agricultural metrics.
- Generate alerts and recommendations.
- Display live and historical information.
- Track treatment/intervention.
- Provide APIs for edge devices.
- Support synchronization after connectivity loss.

---

# 3. Data Contract Convention

Every hardware-derived or software field in this PRD must explicitly identify its source and format.

## 3.1 Rover-populated data format

<span style="color:gray">**Rover-populated data: from Raspberry Pi / AMB82-MINI / GPS / sensors → backend in JSON format.**</span>

Example:

```json
{
  "device_id": "rover-001",
  "timestamp": "2026-09-08T10:42:31Z",
  "gps": {
    "latitude": 13.012345,
    "longitude": 80.123456,
    "accuracy_m": 2.8,
    "altitude_m": 18.2,
    "speed_mps": 0.42,
    "heading_deg": 91.4
  },
  "camera": {
    "camera_id": "amb82-001",
    "frame_id": "frame-008921",
    "image_uri": "edge://frames/frame-008921"
  },
  "cnn": {
    "class": "early_blight",
    "confidence": 0.93,
    "severity": null
  },
  "rover": {
    "status": "SCANNING",
    "sprayer_status": "OFF"
  }
}
```

The exact hardware protocol can change, but the backend contract should preserve equivalent semantic fields.

## 3.2 Software-populated data

Examples:

<span style="color:gray">**Software data: field_id — source: farmer/frontend → backend; format: UUID/string.**</span>

<span style="color:gray">**Software data: zone_id — source: zoning engine → backend; format: UUID/string.**</span>

<span style="color:gray">**Software data: alert_id — source: alert engine → database; format: UUID/string.**</span>

## 3.3 Derived-data format

For every derived field the PRD shall specify:

1. Derived data.
2. Source.
3. Output format.
4. Calculation.
5. Required raw data.

Example:

<span style="color:gray">**Derived data: disease prevalence — source: backend analytics; format: percentage. Calculation: disease-positive observations ÷ total relevant observations × 100. Raw data required: CNN detection records + observation records + timestamps + field/zone IDs.**</span>

---

# 4. User and Authentication Management

The farmer must be able to securely access their farms and equipment.

### Required functionality

1. Register/login.
2. Manage farmer profile.
3. Associate farms with the account.
4. Ensure one farmer cannot access another farmer's farm data.
5. Support future cooperative/enterprise roles.
6. Support device authentication for Raspberry Pi/rover connections.

### Data

<span style="color:gray">**Data: farmer_id, name, phone/email, authentication credentials/status — source: farmer/frontend → backend; format: UUID + strings + securely managed authentication credentials.**</span>

<span style="color:gray">**Data: device_id, device_secret/auth token, device status — source: rover/Raspberry Pi registration → backend; format: UUID/string + secure credential/token.**</span>

---

# 5. Farm Management

The farmer can create one or more farms.

### Required functionality

- Create farm.
- Name farm.
- Store approximate farm location.
- Add fields.
- View farm summary.
- Edit/archive farm.

### Data

<span style="color:gray">**Data: farm_id — source: backend-generated; format: UUID.**</span>

<span style="color:gray">**Data: farm_name — source: farmer → frontend → backend; format: string.**</span>

<span style="color:gray">**Data: farm_location — source: farmer/map → backend; format: latitude/longitude or geographic point.**</span>

---

# 6. Field Creation and Crop Configuration

The farmer creates individual fields within a farm.

### Required functionality

- Field name.
- Crop type.
- Optional crop variety.
- Planting date.
- Expected harvest date.
- Crop growth-stage configuration.
- Field boundary.
- Associated rover(s).

### Data

<span style="color:gray">**Data: field_id — source: backend-generated; format: UUID.**</span>

<span style="color:gray">**Data: crop_type, crop_variety, planting_date — source: farmer → frontend → backend; format: string/date.**</span>

---

# 7. Field Boundary Mapping

The farmer must be able to define where the field physically exists.

### Farmer experience

1. Open "Add Field".
2. Application displays an interactive map/satellite view.
3. Farmer taps/clicks points around the field.
4. Application closes the shape into a polygon.
5. Farmer saves the boundary.
6. Application calculates approximate field area.

The farmer does not need to understand GIS or polygon terminology.

### Map

The implementation may use Google Maps, Mapbox, OpenStreetMap-based services, or another mapping provider.

### Important

The map is only the visualization/input interface. The actual field is stored as geographic coordinates.

### Data

<span style="color:gray">**Data: field_boundary — source: farmer → map frontend → backend; format: GeoJSON Polygon / array of latitude-longitude coordinate pairs.**</span>

<span style="color:gray">**Derived data: field_area — source: geospatial backend; format: m²/hectares. Calculation: geodesic area of stored field polygon. Raw data required: field_boundary coordinates.**</span>

---

# 8. Automatic Field Zoning

The software, not the farmer, creates the initial zones.

### Required functionality

- Take field polygon.
- Generate a configurable grid.
- Clip grid cells to field polygon.
- Assign unique zone IDs.
- Display zone boundaries.
- Allow zone resolution to be changed.
- Support irregular field boundaries.

Example:

```text
┌────────┬────────┬────────┐
│ Z1     │ Z2     │ Z3     │
├────────┼────────┼────────┤
│ Z4     │ Z5     │ Z6     │
├────────┼────────┼────────┤
│ Z7     │ Z8     │ Z9     │
└────────┴────────┴────────┘
```

The default zone size should be configurable, e.g. 5 m × 5 m or 10 m × 10 m.

### Data

<span style="color:gray">**Data: zone_id, zone_polygon, zone_resolution — source: zoning engine using field boundary + configuration; format: UUID + GeoJSON Polygon + numeric dimensions.**</span>

<span style="color:gray">**Derived data: zone_area — source: geospatial backend; format: m². Calculation: geographic area of zone polygon. Raw data required: zone_polygon.**</span>

---

# 9. Rover Registration and Field Association

The farmer can connect a rover to the software.

### Required functionality

- Register rover.
- Assign unique device ID.
- Pair rover with account.
- Associate rover with one or more fields.
- Show online/offline state.
- Show last communication.
- Show current operation state.

### Data

<span style="color:gray">**Rover-populated data: device_id, firmware_version, battery_level, rover_status, timestamp — source: Raspberry Pi / rover controller → backend; format: JSON with string/number fields.**</span>

<span style="color:gray">**Software data: field_rover_assignment — source: farmer/frontend → backend; format: relational association between rover_id and field_id.**</span>

---

# 10. Rover Position Tracking

The backend shall receive the rover's position continuously or at a configured interval.

### Required functionality

- Receive GPS position.
- Validate coordinates.
- Store timestamp.
- Display current position.
- Draw rover route.
- Determine field containing rover.
- Determine zone containing rover.
- Detect movement outside field boundary.
- Maintain route history.

### Data

<span style="color:gray">**Rover-populated data: latitude, longitude, GPS accuracy, altitude, speed, heading, timestamp — source: GPS/GNSS → Raspberry Pi → backend; format: JSON numeric fields + ISO-8601 timestamp.**</span>

<span style="color:gray">**Derived data: current_field_id — source: geospatial backend; format: UUID/null. Calculation: point-in-polygon test between rover GPS coordinate and saved field polygon. Raw data required: rover latitude/longitude + field_boundary.**</span>

<span style="color:gray">**Derived data: current_zone_id — source: geospatial backend; format: UUID/null. Calculation: point-in-polygon test between rover GPS coordinate and zone polygon. Raw data required: rover latitude/longitude + zone polygons.**</span>

---

# 11. Rover Route History

The application shall store the path followed during a scan.

### Data

<span style="color:gray">**Rover-populated data: timestamped GPS positions — source: GPS → Raspberry Pi → backend; format: JSON array/events containing latitude, longitude, timestamp.**</span>

<span style="color:gray">**Derived data: rover_route — source: backend; format: GeoJSON LineString. Calculation: order timestamped GPS points by time and construct a line. Raw data required: GPS position samples.**</span>

<span style="color:gray">**Derived data: distance_travelled — source: backend; format: metres/km. Calculation: sum geographic distance between consecutive valid GPS points. Raw data required: ordered GPS coordinates.**</span>

---

# 12. Scan Session Management

Every rover field operation should be represented as a scan session.

### Required functionality

- Start scan.
- End scan.
- Associate scan with field and rover.
- Store route.
- Count observations.
- Count detections.
- Track visited zones.
- Track treatments.
- Track interruptions.

### Data

<span style="color:gray">**Rover-populated data: scan_start, scan_end, rover status events — source: Raspberry Pi/rover controller → backend; format: JSON event with timestamp and device_id.**</span>

<span style="color:gray">**Derived data: scan_duration — source: backend; format: seconds/minutes. Calculation: scan_end_timestamp − scan_start_timestamp. Raw data required: scan start/end events.**</span>

<span style="color:gray">**Derived data: zones_visited — source: backend; format: array of zone_ids. Calculation: unique zone IDs associated with timestamped rover positions during session. Raw data required: GPS positions + zone polygons.**</span>

---

# 13. Camera Observation Pipeline

Every image/frame processed by the CNN should be represented as an observation.

### Required data

<span style="color:gray">**Rover-populated data: frame_id, camera_id, image/frame reference, timestamp — source: AMB82-MINI → Raspberry Pi → backend; format: JSON metadata + image URI/reference.**</span>

<span style="color:gray">**Rover-populated data: capture latitude/longitude — source: GPS/Raspberry Pi at capture time → backend; format: numeric latitude/longitude in JSON.**</span>

### Required association

Each observation should link to:

- Rover.
- Scan session.
- Field.
- Zone.
- Timestamp.
- Camera frame.
- CNN inference.

---

# 14. CNN Disease Detection

The system shall record visible crop disease detections.

### Required functionality

- Disease class.
- Confidence.
- Location.
- Timestamp.
- Image/frame.
- Field.
- Zone.
- Optional bounding box/segmentation.
- Severity if the model provides it or if software derives it.

### Data

<span style="color:gray">**Rover-populated data: CNN class, confidence, model_version, optional bounding_box, frame_id — source: CNN running on edge device → Raspberry Pi → backend; format: JSON.**</span>

Example:

```json
{
  "class": "early_blight",
  "confidence": 0.93,
  "model_version": "tomato-v1",
  "bounding_box": [120, 80, 410, 390]
}
```

<span style="color:gray">**Derived data: detection_zone_id — source: backend geospatial service; format: UUID. Calculation: detection GPS coordinate → point-in-polygon against zone polygons. Raw data required: detection latitude/longitude + zone_polygon.**</span>

---

# 15. Pest Detection and Early Warning

The system shall detect pests and identify infestation patterns.

### Required functionality

- Pest class.
- Confidence.
- Location.
- Timestamp.
- Field/zone.
- Detection frequency.
- Spatial concentration.
- Increasing/decreasing activity.
- Early warning.

### Data

<span style="color:gray">**Rover-populated data: pest_class, confidence, frame_id, latitude, longitude, timestamp — source: AMB82-MINI + CNN + GPS → Raspberry Pi → backend; format: JSON.**</span>

<span style="color:gray">**Derived data: pest_detection_count — source: backend analytics; format: integer. Calculation: count valid pest detections for selected field/zone/time period. Raw data required: pest detection records.**</span>

<span style="color:gray">**Derived data: pest_activity_trend — source: backend analytics; format: increasing/stable/decreasing + percentage change. Calculation: compare detection rate across two comparable time windows. Raw data required: timestamped pest detections + observation/session counts.**</span>

---

# 16. Disease/Pest Prevalence and Zone Classification

The software shall classify problem severity at zone level.

### Important

The farmer should NOT be required to manually enter the number of plants for the initial system.

The first version should classify based on observed data.

### Example

If a zone has:

- 100 relevant observations.
- 5 disease-positive observations.

Then:

`Prevalence = 5 / 100 × 100 = 5%`

### Data

<span style="color:gray">**Derived data: disease_prevalence — source: backend analytics; format: percentage. Calculation: disease-positive relevant observations ÷ total relevant observations × 100. Raw data required: CNN detections + observations + zone_id.**</span>

<span style="color:gray">**Derived data: pest_prevalence — source: backend analytics; format: percentage. Calculation: pest-positive relevant observations ÷ total relevant observations × 100. Raw data required: pest detections + observations + zone_id.**</span>

<span style="color:gray">**Derived data: zone_risk_level — source: rules/analytics engine; format: LOW/MODERATE/HIGH/CRITICAL. Calculation: configurable thresholds over prevalence, confidence, trend, and optionally severity. Raw data required: detection counts, observation counts, confidence, trends.**</span>

Future plant-level version:

<span style="color:gray">**Derived data: plant_infestation_rate — source: plant-counting/plant-identification model + CNN; format: percentage. Calculation: affected plants ÷ inspected plants × 100. Raw data required: unique plant IDs/count + affected plant IDs.**</span>

---

# 17. Spatial Hotspot Detection

The software shall determine where detections are concentrated.

### Required functionality

- Display individual detections.
- Aggregate nearby detections.
- Identify hotspots.
- Display hotspot severity.
- Allow drill-down into raw detections.

### Data

<span style="color:gray">**Derived data: hotspot — source: backend geospatial analytics; format: GeoJSON Point/Polygon + severity. Calculation: spatial clustering/density analysis over timestamped detection coordinates. Raw data required: detection latitude/longitude + detection class + timestamps.**</span>

<span style="color:gray">**Derived data: hotspot_density — source: backend analytics; format: detections/km² or configured density unit. Calculation: relevant detections ÷ geographical area of hotspot. Raw data required: detection coordinates + hotspot geometry.**</span>

---

# 18. Crop Health Monitoring

The system shall provide overall crop-health monitoring.

### Inputs

- Disease detections.
- Pest detections.
- Nutrient-deficiency detections.
- Water stress.
- Environmental stress.
- Crop growth stage.

### Data

<span style="color:gray">**Derived data: field_health_status — source: backend health scoring engine; format: score + LOW/MODERATE/GOOD/CRITICAL status. Calculation: configurable weighted aggregation of validated health indicators. Raw data required: disease/pest/nutrient/water/environmental metrics.**</span>

The exact weighting must be configurable rather than hardcoded before model validation.

---

# 19. Nutrient Deficiency Monitoring

The system shall support nutrient-deficiency detection through color, texture, growth analysis, and future sensor integration where available.

### Data

<span style="color:gray">**Rover-populated data: image/frame + CNN nutrient-deficiency class + confidence + location — source: AMB82-MINI + CNN + GPS → Raspberry Pi → backend; format: JSON.**</span>

<span style="color:gray">**Derived data: nutrient_risk — source: backend analytics; format: LOW/MODERATE/HIGH + suspected deficiency. Calculation: thresholding/aggregation of model detections and confidence over a zone/time window. Raw data required: nutrient detections + confidence + location + zone.**</span>

The UI must clearly distinguish a model indication from a laboratory-confirmed nutrient diagnosis.

---

# 20. Crop Growth-Stage Monitoring

The application shall monitor crop growth stages where the available model/data supports it.

### Required functionality

- Record farmer-provided planting date.
- Record model-detected growth stage when available.
- Compare expected and observed growth stage.
- Display growth-stage history.

### Data

<span style="color:gray">**Data: planting_date — source: farmer → frontend → backend; format: ISO date.**</span>

<span style="color:gray">**Rover-populated data: plant/field image + growth-stage model output + confidence + timestamp — source: AMB82-MINI + edge CNN → Raspberry Pi → backend; format: JSON.**</span>

<span style="color:gray">**Derived data: growth_stage_status — source: backend; format: ON_TRACK/EARLY/DELAYED/UNKNOWN. Calculation: compare observed growth stage with expected crop stage based on crop configuration and planting date. Raw data required: planting_date + crop configuration + observed growth stage.**</span>

---

# 21. Soil Moisture Monitoring

The application shall display soil moisture and use it in irrigation decisions.

### Data

<span style="color:gray">**Rover-populated data: soil_moisture, sensor_id, timestamp, location — source: soil-moisture sensor → Raspberry Pi → backend; format: JSON numeric reading + sensor metadata.**</span>

<span style="color:gray">**Derived data: moisture_status — source: backend rules engine; format: DRY/ADEQUATE/WET/UNKNOWN. Calculation: compare normalized sensor value against crop/soil thresholds. Raw data required: soil_moisture + crop/soil thresholds.**</span>

---

# 22. Temperature and Humidity Monitoring

### Data

<span style="color:gray">**Rover-populated data: air_temperature, relative_humidity, sensor_id, timestamp, location — source: environmental sensors → Raspberry Pi → backend; format: JSON numeric fields.**</span>

<span style="color:gray">**Derived data: heat_stress_level — source: backend risk engine; format: NONE/LOW/MODERATE/HIGH/CRITICAL. Calculation: evaluate temperature and relevant duration against configured crop-specific thresholds. Raw data required: timestamped temperature + crop configuration + optional humidity.**</span>

---

# 23. Smart Irrigation Management

The application shall determine whether irrigation is currently recommended.

### Required functionality

- Show soil moisture.
- Show weather.
- Detect water stress.
- Detect over-irrigation.
- Recommend irrigation timing.
- Track irrigation decisions.
- Support irrigation-equipment integration.

### Data

<span style="color:gray">**Derived data: irrigation_recommendation — source: irrigation decision engine; format: IRRIGATE_NOW/IRRIGATE_SOON/DELAY/NO_IRRIGATION/UNKNOWN. Calculation: evaluate soil moisture + temperature + humidity + weather + crop stage + configured thresholds. Raw data required: sensor readings + weather + crop metadata.**</span>

<span style="color:gray">**Derived data: water_stress_status — source: backend analytics; format: NONE/LOW/MODERATE/HIGH. Calculation: combine low soil moisture, environmental demand, and persistence over time. Raw data required: soil moisture + temperature + humidity + timestamps + crop configuration.**</span>

<span style="color:gray">**Derived data: over_irrigation_status — source: backend analytics; format: NORMAL/POSSIBLE_OVER_IRRIGATION/HIGH_RISK. Calculation: identify excessive moisture or irrigation duration/volume relative to configured thresholds. Raw data required: soil moisture + irrigation events + weather + crop configuration.**</span>

---

# 24. Weather Integration

The backend shall support external weather data because the problem statement explicitly requires weather conditions for irrigation and environmental-risk decisions.

### Required data

<span style="color:gray">**Data: current temperature, humidity, rainfall, forecast rainfall, weather condition, timestamp — source: external weather API/service → backend; format: normalized JSON.**</span>

The specific weather provider is an implementation decision.

---

# 25. Environmental Risk Monitoring

The application shall monitor:

- Drought.
- Excessive rainfall.
- Flooding.
- Heat waves/heat stress.
- Disease-outbreak environmental conditions.
- Other abnormal environmental patterns.

### Data

<span style="color:gray">**Derived data: drought_risk — source: environmental risk engine; format: LOW/MODERATE/HIGH/CRITICAL. Calculation: configurable analysis of soil moisture + rainfall/weather history + temperature and persistence. Raw data required: soil moisture + rainfall + temperature + timestamps.**</span>

<span style="color:gray">**Derived data: flood_risk — source: environmental risk engine; format: LOW/MODERATE/HIGH/CRITICAL. Calculation: configurable analysis of rainfall, forecast rainfall, local moisture/water-level inputs where available, and field risk configuration. Raw data required: rainfall/weather + sensor data where available + field metadata.**</span>

<span style="color:gray">**Derived data: heat_risk — source: environmental risk engine; format: LOW/MODERATE/HIGH/CRITICAL. Calculation: temperature/heat exposure against crop-specific thresholds and duration. Raw data required: temperature time series + crop configuration.**</span>

<span style="color:gray">**Derived data: disease_environment_risk — source: backend risk engine; format: LOW/MODERATE/HIGH. Calculation: combine environmental conditions associated with the configured crop/disease with observed detection trends. Raw data required: weather/environmental time series + disease detections.**</span>

---

# 26. Localized Field-Level Alerts

All important risks should be localized to the affected field/zone whenever the available data supports it.

### Alert examples

- Possible disease detected.
- Pest activity increasing.
- High pest concentration in Zone 5.
- Irrigate now.
- Delay irrigation.
- Heat-stress warning.
- Flood-risk alert.
- Drought-risk alert.
- Possible nutrient deficiency.

### Data

<span style="color:gray">**Derived data: alert — source: backend rules/risk engine; format: JSON/database record containing alert_id, type, severity, field_id, optional zone_id, message, timestamp, status. Raw data required: relevant detection/sensor/weather/analytics data.**</span>

---

# 27. Farmer Advisory System

The software shall translate technical analytics into simple farmer-facing actions.

### Required output structure

Every advisory should answer:

1. What is happening?
2. Where?
3. How serious?
4. What should the farmer do?
5. Has action already been taken?

### Data

<span style="color:gray">**Derived data: advisory — source: recommendation/rules engine; format: structured JSON/database record. Calculation: map detected condition/risk to a validated recommendation rule. Raw data required: alert/detection/irrigation/environmental metrics + crop configuration.**</span>

Example:

`Possible disease detected in Zone 5. Inspect/treat the affected area.`

The system should not claim a definitive agronomic diagnosis when the model only provides a probability.

---

# 28. Targeted Pesticide/Spray Intervention

The software shall support targeted intervention rather than blanket pesticide application.

### Required functionality

- Identify problem locations.
- Determine affected zones.
- Show recommended intervention locations.
- Send/record spray commands/events.
- Record actual treatment.
- Compare detections against treated areas.

### Data

<span style="color:gray">**Derived data: spray_recommendation — source: backend intervention engine; format: JSON containing field_id, zone_id, target locations, reason, priority, recommended action. Calculation: map qualifying disease/pest detections to configured intervention rules. Raw data required: CNN detections + GPS + zone + severity/prevalence + intervention rules.**</span>

---

# 29. Spray Event Tracking

The software must know what the rover actually did, not merely what it was told to do.

### Data

<span style="color:gray">**Rover-populated data: spray_status, spray_start, spray_end, spray_duration, spray_location, flow/quantity where available — source: sprayer hardware → Raspberry Pi → backend; format: JSON.**</span>

Example:

```json
{
  "device_id": "rover-001",
  "event": "SPRAY_COMPLETED",
  "timestamp": "2026-09-08T10:47:22Z",
  "location": {
    "latitude": 13.012401,
    "longitude": 80.123510
  },
  "duration_seconds": 2.5,
  "quantity_ml": 35
}
```

If the hardware does not provide quantity, the backend must not invent it.

---

# 30. Treatment Coverage

The application shall compare problem detections with treatment events.

### Data

<span style="color:gray">**Derived data: treatment_coverage — source: backend geospatial analytics; format: percentage. Calculation: qualifying detected locations that fall within treated locations/coverage area ÷ qualifying detected locations × 100. Raw data required: detection coordinates + treatment coordinates/coverage geometry + timestamps.**</span>

<span style="color:gray">**Derived data: untreated_problem_count — source: backend analytics; format: integer. Calculation: qualifying detections with no corresponding treatment event within configured spatial/time criteria. Raw data required: detections + treatment events + coordinates + timestamps.**</span>

---

# 31. Irrigation Event Tracking

If irrigation equipment is integrated, the software shall track irrigation actions.

### Data

<span style="color:gray">**Rover/equipment-populated data: irrigation_start, irrigation_end, irrigation_status, location/zone, water_volume where available — source: irrigation controller/pump/sensor → Raspberry Pi or integration gateway → backend; format: JSON.**</span>

<span style="color:gray">**Derived data: irrigation_duration — source: backend; format: seconds/minutes. Calculation: end timestamp − start timestamp. Raw data required: irrigation start/end events.**</span>

<span style="color:gray">**Derived data: water_used — source: backend or flow meter integration; format: litres. Calculation: direct flow-meter reading or flow_rate × duration when validated. Raw data required: flow rate/volume telemetry + irrigation duration.**</span>

---

# 32. Water-Usage Efficiency

The dashboard should demonstrate the problem statement's goal of minimizing water consumption.

### Data

<span style="color:gray">**Derived data: water_usage_per_area — source: backend analytics; format: litres/m² or litres/hectare. Calculation: total measured irrigation water ÷ treated/irrigated field area. Raw data required: water-volume readings + irrigation area.**</span>

<span style="color:gray">**Derived data: irrigation_saving_estimate — source: backend analytics; format: litres + percentage. Calculation: baseline/reference water usage − actual/recommended usage, where a valid baseline exists. Raw data required: historical/baseline irrigation data + actual water usage.**</span>

---

# 33. Field Health Map

The map is the primary spatial dashboard.

### Layers

- Field boundary.
- Zones.
- Rover position.
- Rover route.
- Disease detections.
- Pest detections.
- Nutrient-deficiency detections.
- Water-stress areas.
- Environmental risk.
- Hotspots.
- Spray/treatment locations.
- Irrigation locations.

### Data

<span style="color:gray">**Software data: map layers — source: backend geospatial data + analytics; format: GeoJSON/features or equivalent map-provider objects.**</span>

<span style="color:gray">**Rover-populated data displayed on map: rover GPS, detections, spray events, sensor readings — source: Raspberry Pi/AMB82-MINI/GPS/sensors → backend → frontend JSON.**</span>

---

# 34. Live Rover Dashboard

The farmer should be able to monitor an active rover.

### Display

- Current rover position.
- Current field.
- Current zone.
- Rover status.
- Battery if available.
- Latest CNN result.
- Latest image/frame if available.
- Sensor values.
- Sprayer status.
- Connection status.
- Last update time.

### Data

<span style="color:gray">**Rover-populated data: battery_level, rover_status, latitude, longitude, speed, heading, current sensor values, camera/CNN event, spray_status — source: Raspberry Pi + GPS + sensors + AMB82-MINI + rover controller → backend; format: JSON.**</span>

---

# 35. Detection Detail Screen

When the farmer selects a detection:

### Display

- Disease/pest/deficiency.
- Confidence.
- Image.
- Timestamp.
- Location.
- Zone.
- Rover.
- Scan session.
- Severity/risk.
- Treatment status.

### Data

<span style="color:gray">**Data: detection detail — source: stored CNN observation + GPS + zone mapping + treatment database; format: JSON API response.**</span>

---

# 36. Zone Detail Screen

Selecting a zone should provide an aggregated summary.

### Display

- Zone ID/name.
- Area.
- Disease detections.
- Pest detections.
- Nutrient issues.
- Water stress.
- Environmental risk.
- Prevalence.
- Trend.
- Risk level.
- Treatment status.
- Last scan.

### Data

<span style="color:gray">**Derived data: zone_summary — source: backend aggregation; format: JSON. Calculation: aggregate raw observations, detections, sensors, alerts, and treatments by zone and time window. Raw data required: all corresponding zone-linked records.**</span>

---

# 37. Farm Analytics Dashboard

The application shall provide historical analytics.

### Required charts/metrics

- Crop-health trend.
- Disease detections over time.
- Pest detections over time.
- Nutrient-deficiency trends.
- Water-stress trends.
- Soil moisture.
- Temperature.
- Humidity.
- Rainfall/weather.
- Irrigation history.
- Treatment history.
- Zone comparisons.
- Risk history.

### Data

<span style="color:gray">**Derived data: time-series metrics — source: backend analytics/database; format: timestamp + numeric/status value. Calculation: aggregate raw observations into daily/hourly/scan-level metrics. Raw data required: timestamped detections, sensors, weather, irrigation, treatment events.**</span>

---

# 38. Yield-Risk Forecasting

The problem statement requires yield-risk forecasting and decision-support insights.

The initial software should expose a **yield-risk indicator**, not claim an exact yield prediction unless a validated prediction model and sufficient training data exist.

### Inputs

- Disease prevalence.
- Pest prevalence.
- Water stress.
- Heat stress.
- Environmental risk.
- Growth-stage status.
- Historical trends.
- Treatment response.

### Data

<span style="color:gray">**Derived data: yield_risk — source: backend risk/ML model; format: LOW/MODERATE/HIGH/CRITICAL + optional probability/score. Calculation: model/rules-based aggregation of validated risk variables. Raw data required: disease/pest/water/environment/growth/treatment history.**</span>

---

# 39. Decision-Support Insights

The application should identify important changes instead of making the farmer inspect every graph.

### Examples

- Disease increasing in Zone 4.
- Pest activity spreading toward Zone 5.
- Water stress increasing.
- Heat conditions becoming risky.
- Recently treated zone showing reduced detections.
- Untreated high-risk zone remaining active.

### Data

<span style="color:gray">**Derived data: decision_insight — source: analytics/rules engine; format: structured insight record with type, severity, field_id, zone_id, evidence, and recommended action. Calculation: compare current analytics with historical baselines/thresholds. Raw data required: time-series detections + sensor/weather/treatment records.**</span>

---

# 40. Notification System

### Channels

- In-app notification.
- Dashboard alert.
- Push notification.
- SMS, where implemented.

### Data

<span style="color:gray">**Data: notification — source: alert engine → notification service → farmer; format: JSON containing notification_id, alert_id, channel, recipient, timestamp, delivery status.**</span>

---

# 41. Offline / Intermittent Connectivity

The system must not depend on continuous internet connectivity for edge AI operation.

### Required behavior

When internet is unavailable:

1. Rover continues collecting data.
2. CNN continues local inference.
3. Raspberry Pi queues events.
4. Data is transmitted when connectivity returns.
5. Backend deduplicates events.
6. Historical timestamps are preserved.

### Data

<span style="color:gray">**Rover-populated data: locally queued observations/events — source: Raspberry Pi local storage; format: same JSON event contract with event_id and original timestamp.**</span>

<span style="color:gray">**Derived data: synchronization_status — source: backend/device sync service; format: QUEUED/SYNCED/FAILED/PARTIAL. Calculation: compare edge event IDs with backend acknowledgement records. Raw data required: event_id + sync acknowledgements.**</span>

---

# 42. Edge-to-Backend Synchronization

### Required functionality

- Authenticate device.
- Accept batched events.
- Validate schema.
- Validate timestamp.
- Validate GPS.
- Store raw event.
- Process event.
- Return acknowledgement.
- Support retry.
- Prevent duplicate processing.

### API example

```http
POST /api/v1/edge/events
```

```json
{
  "event_id": "evt-000123",
  "device_id": "rover-001",
  "timestamp": "2026-09-08T10:42:31Z",
  "event_type": "CNN_DETECTION",
  "payload": {}
}
```

<span style="color:gray">**Rover-populated data: event_id, device_id, timestamp, event_type, payload — source: Raspberry Pi → backend API; format: JSON.**</span>

---

# 43. Core Backend Entities

The backend should initially model at least:

- User/Farmer.
- Farm.
- Field.
- Field Boundary.
- Crop.
- Zone.
- Rover.
- Rover Position.
- Scan Session.
- Camera.
- Camera Observation.
- CNN Model.
- CNN Detection.
- Pest.
- Disease.
- Nutrient Deficiency.
- Environmental Reading.
- Weather Observation.
- Irrigation Recommendation.
- Irrigation Event.
- Spray Recommendation.
- Spray Event.
- Alert.
- Advisory.
- Treatment Coverage.
- Health/Risk Summary.

---

# 44. Core Relationship Model

```text
FARMER
  │
  └── FARM
       │
       └── FIELD
            │
            ├── FIELD BOUNDARY
            │
            ├── ZONES
            │
            ├── SCAN SESSIONS
            │     │
            │     └── ROVER POSITIONS
            │
            ├── CAMERA OBSERVATIONS
            │     │
            │     └── CNN DETECTIONS
            │
            ├── ENVIRONMENTAL READINGS
            │
            ├── IRRIGATION EVENTS
            │
            ├── SPRAY EVENTS
            │
            └── ALERTS / ADVISORIES / ANALYTICS
```

---

# 45. Detection-to-Zone Processing Pipeline

This is a core backend workflow.

```text
AMB82-MINI
    ↓
Image/frame
    ↓
CNN
    ↓
Prediction
    ↓
Raspberry Pi
    ↓
GPS + timestamp + rover ID
    ↓
Backend
    ↓
Field point-in-polygon
    ↓
Zone point-in-polygon
    ↓
Store detection
    ↓
Update zone analytics
    ↓
Update hotspot
    ↓
Update alert
    ↓
Update dashboard
```

### Data

<span style="color:gray">**Rover-populated raw data: image/frame reference + CNN output + GPS + timestamp + rover_id — source: AMB82-MINI/CNN/GPS/Raspberry Pi; format: JSON event.**</span>

<span style="color:gray">**Derived data: field_id + zone_id — source: backend geospatial engine; format: UUIDs. Calculation: point-in-polygon using detection GPS coordinate. Raw data required: latitude/longitude + stored field/zone polygons.**</span>

---

# 46. Dashboard Home

The first screen should summarize the farmer's operation.

### Display

- Total fields.
- Fields requiring attention.
- Active disease/pest alerts.
- Water-stress alerts.
- Environmental-risk alerts.
- Rover status.
- Latest detections.
- Latest recommendations.

### Data

<span style="color:gray">**Derived data: dashboard_summary — source: backend aggregation service; format: JSON. Calculation: aggregate current field/zone alerts, rover state, detection state, environmental state, and recommendations. Raw data required: corresponding live/current records.**</span>

---

# 47. Field Health Status

Every field should have a simple current status.

### Suggested statuses

- Healthy.
- Monitor.
- Attention required.
- High risk.
- Critical.

### Data

<span style="color:gray">**Derived data: field_risk_status — source: backend risk engine; format: categorical status + numeric score where applicable. Calculation: configured weighted aggregation of active zone risks, disease/pest prevalence, water stress, and environmental risks. Raw data required: zone risk metrics + field-level environmental/sensor metrics.**</span>

---

# 48. Historical Treatment Effectiveness

Where sufficient repeated observations exist, the application should compare conditions before and after treatment.

### Data

<span style="color:gray">**Derived data: treatment_response — source: backend analytics; format: IMPROVING/UNCHANGED/WORSENING/INSUFFICIENT_DATA. Calculation: compare detection prevalence/rate before and after treatment over a configured time window. Raw data required: timestamped detections + treatment timestamps + zone/location.**</span>

This should be presented as an observational software metric, not proof that a treatment caused the change.

---

# 49. Search, Filters, and Drill-Down

The farmer should be able to filter:

- Field.
- Zone.
- Crop.
- Disease.
- Pest.
- Nutrient issue.
- Risk type.
- Date/time.
- Rover.
- Scan session.
- Treatment status.
- Alert severity.

### Data

<span style="color:gray">**Data: filter parameters — source: farmer/frontend → backend query API; format: URL/query JSON parameters.**</span>

---

# 50. Scalability

The architecture must support:

- One farmer → one field.
- One farmer → multiple fields.
- Multiple rovers.
- Cooperatives.
- Large agricultural organizations.
- Multiple crop types.
- Multiple CNN models.
- Multiple sensor types.

The software should use IDs and relationships rather than hardcoded assumptions about one rover, one field, or one crop.

### Data

<span style="color:gray">**Software data: tenant/user/farm/field/device relationships — source: backend database; format: relational/document entities using UUIDs and foreign-key/reference relationships.**</span>

---

# 51. Farm Equipment Integration

The problem statement requires integration with farm equipment.

The initial architecture should expose integration interfaces for:

- Sprayer.
- Irrigation controller.
- Pump.
- Other supported equipment.

### Data

<span style="color:gray">**Equipment-populated data: equipment_id, status, command_acknowledgement, operating_start/end, location where available, quantity/flow where available — source: equipment controller/Raspberry Pi/integration gateway → backend; format: JSON events.**</span>

---

# 52. Backend API Categories

The backend should expose APIs for:

### Authentication
- Login.
- User profile.

### Farm
- Create/read/update/archive farm.

### Field
- Create/read/update/archive field.
- Boundary management.

### Zones
- Generate zones.
- Retrieve zones.
- Update zoning configuration.

### Rover
- Register.
- Pair.
- Status.
- Position.

### Edge ingestion
- Sensor events.
- Camera observations.
- CNN detections.
- Spray events.
- Irrigation events.

### Analytics
- Field health.
- Zone health.
- Pest/disease prevalence.
- Hotspots.
- Water stress.
- Environmental risk.
- Yield risk.

### Alerts
- Current alerts.
- Historical alerts.
- Acknowledgement.

### Recommendations
- Current recommendations.
- Recommendation history.

---

# 53. Raw Data vs Derived Data Rule

The backend must preserve raw hardware observations separately from calculated values.

### Example

Do NOT store only:

`Zone 5 = HIGH DISEASE`

Store:

```text
Raw:
- image/frame
- CNN class
- confidence
- GPS
- timestamp
- rover ID

Derived:
- field ID
- zone ID
- detection count
- prevalence
- hotspot
- risk level
- advisory
```

<span style="color:gray">**Raw-data source: hardware/edge systems. Derived-data source: backend analytics/geospatial/rules engines.**</span>

This allows thresholds and algorithms to be changed later without losing the underlying evidence.

---

# 54. Model Versioning

Every CNN-derived result should record which model generated it.

### Data

<span style="color:gray">**Rover-populated data: model_version, model_name, inference_timestamp, class, confidence — source: CNN/edge inference → Raspberry Pi → backend; format: JSON.**</span>

This is required so historical results remain interpretable after the CNN is updated.

---

# 55. Data Validation

The backend must validate incoming edge data.

### Validate

- Required event fields.
- Device authentication.
- Timestamp.
- GPS ranges.
- Confidence range 0–1.
- Sensor value ranges.
- Duplicate event IDs.
- Unknown devices.
- Unknown fields/zones.
- Malformed JSON.

Invalid events should be rejected or quarantined without corrupting agricultural analytics.

---

# 56. Minimum Viable Product

The first implementation should prioritize:

1. Farmer authentication.
2. Farm creation.
3. Field creation.
4. Interactive map.
5. Field boundary drawing.
6. Automatic zone generation.
7. Rover registration.
8. Raspberry Pi API.
9. GPS ingestion.
10. Live rover map position.
11. AMB82-MINI/CNN event ingestion.
12. Disease/pest detection records.
13. Detection-to-field mapping.
14. Detection-to-zone mapping.
15. Zone-level counts/prevalence.
16. Basic hotspot visualization.
17. Spray-event tracking.
18. Treated vs untreated visualization.
19. Basic soil/environmental sensor ingestion.
20. Irrigation recommendation engine.
21. Environmental alerts.
22. Farmer advisories.
23. Historical analytics.
24. Offline event queue and synchronization.
25. Basic field-health/risk dashboard.

---

# 57. Phase 2

After the MVP:

- Plant-level identification.
- More sophisticated spatial clustering.
- Improved infestation estimation.
- Crop-specific agronomic models.
- Advanced nutrient analysis.
- Advanced irrigation optimization.
- Automated path planning integration.
- More accurate spray-coverage estimation.
- Yield prediction model.
- Treatment-response modelling.
- Cooperative/enterprise management.
- SMS/push expansion.
- More equipment integrations.

---

# 58. Important Technical Assumptions / Open Questions

These must be resolved with the hardware/ML team before final implementation.

1. **Positioning:** What GPS/GNSS hardware does the rover use, and what accuracy can it provide?
2. **Camera:** How frequently can the AMB82-MINI provide frames to the CNN?
3. **CNN:** Does the model provide classification only, object detection bounding boxes, or segmentation?
4. **CNN classes:** Which crops, diseases, pests, and nutrient deficiencies are actually supported?
5. **CNN confidence:** Is the confidence score calibrated?
6. **Plant counting:** Can the system identify unique plants, or only image observations?
7. **Sensors:** Which soil/environmental sensors are actually installed?
8. **Sprayer:** Does the hardware provide spray duration, flow, quantity, and exact spray location?
9. **Rover communication:** What communication protocol connects Raspberry Pi to backend?
10. **Connectivity:** What happens when there is no internet for several hours/days?
11. **Weather:** Which weather API/provider will be used?
12. **Irrigation:** Is irrigation only recommended, or can the software control an irrigation system?
13. **Map provider:** Which mapping provider will be selected?
14. **Edge processing:** Exactly which processing occurs on the Raspberry Pi/edge device versus backend?
15. **Hardware command protocol:** What JSON/schema does Raspberry Pi expect for rover/sprayer commands?

---

# 59. End-to-End Product Flow

```text
FARMER
  ↓
Create Farm
  ↓
Create Field
  ↓
Draw Field Boundary
  ↓
Software Calculates Area
  ↓
Software Generates Zones
  ↓
Pair Rover
  ↓
Rover Enters Field
  ↓
GPS → Raspberry Pi
  ↓
Raspberry Pi → Backend
  ↓
AMB82-MINI Captures Frame
  ↓
CNN Runs On-Device
  ↓
CNN Result → Raspberry Pi
  ↓
GPS + CNN + Timestamp + Rover ID
  ↓
Backend
  ↓
Determine Field
  ↓
Determine Zone
  ↓
Store Raw Observation
  ↓
Calculate Disease/Pest/Nutrient/Water Metrics
  ↓
Calculate Hotspots/Risk
  ↓
Generate Advisory/Alert
  ↓
Farmer Dashboard
  ↓
Targeted Treatment
  ↓
Sprayer → Raspberry Pi → Backend
  ↓
Record Treatment
  ↓
Compare Detection vs Treatment
  ↓
Historical Analytics
```

---

# 60. Final Software Product Principle

The application is not merely a dashboard showing CNN predictions.

It is a **geospatial farm intelligence and decision-support system**.

The software must transform:

**Raw edge data**

→ **Location-aware observations**

→ **Field/zone intelligence**

→ **Risk assessment**

→ **Actionable recommendations**

→ **Treatment tracking**

→ **Historical farm intelligence**

The farmer should ultimately be able to answer:

### WHAT is happening?
Disease, pest, nutrient deficiency, water stress, environmental risk.

### WHERE is it happening?
Field → zone → geographical location.

### HOW SERIOUS is it?
Confidence, prevalence, concentration, trend, risk.

### WHAT SHOULD I DO?
Irrigate, inspect, monitor, treat, delay, or take other validated action.

### WHAT HAS ALREADY BEEN DONE?
Sprayed, irrigated, inspected, untreated, or still pending.

This is the software layer that connects the Qualcomm problem statement's edge-AI requirements to a usable farmer-facing product.
