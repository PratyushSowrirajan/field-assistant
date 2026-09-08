# Smart Farming Assistant — UI / Design Rules Specification

**Document type:** UI specification + design rules  
**Primary consumer:** Claude / frontend implementation agent  
**Applies to:** Farmer-facing web application, responsive desktop/tablet/mobile layouts  
**Design reference:** User-provided National Mission on Natural Farming screenshot  
**Functional source:** Smart Farming Assistant Software PRD v2

---

# 1. Design Direction

The Smart Farming Assistant must **look like a farming product first and a software dashboard second**.

The application must not become a generic SaaS/admin dashboard filled with:
- dozens of cards
- tiny charts
- excessive sidebars
- dense tables
- unnecessary pages
- decorative gradients
- generic blue/purple analytics styling
- repeated KPI tiles
- technology-centric visual language

The UI should feel like a **modern digital farm field guide**: practical, calm, geographic, visual, and action-oriented.

The product should communicate:

> **See the field → understand the problem → know where it is → decide what to do → see what has already been done.**

The application still has to expose all required functionality from the PRD. The solution to complexity is **information hierarchy and progressive disclosure**, not removing functionality.

---

# 2. Core Design Principle

The interface must always prioritize five farmer questions:

1. **WHAT is happening?**
   - disease
   - pest
   - nutrient deficiency
   - water stress
   - environmental risk

2. **WHERE is it happening?**
   - farm
   - field
   - zone
   - exact observation location when supported

3. **HOW SERIOUS is it?**
   - confidence
   - prevalence
   - concentration
   - trend
   - risk level

4. **WHAT SHOULD I DO?**
   - inspect
   - irrigate
   - delay irrigation
   - monitor
   - treat
   - take another validated action

5. **WHAT HAS ALREADY BEEN DONE?**
   - sprayed
   - irrigated
   - inspected
   - untreated
   - pending

Do not design screens around database entities. Design screens around these farmer decisions.

---

# 3. Visual Personality

## 3.1 Theme

Use **farming, crops, soil, fields, sunlight, water, and natural materials** as the visual language.

The product should feel connected to:
- agricultural land
- crop rows
- leaves
- soil
- field boundaries
- irrigation
- natural farming
- farm workers
- rural India

It should NOT look like:
- a banking application
- a cybersecurity dashboard
- a generic AI SaaS product
- a cryptocurrency dashboard
- a hospital monitoring system
- a developer admin panel

## 3.2 Emotional tone

The interface should feel:

**Grounded → useful → trustworthy → calm → intelligent → practical**

Avoid:
- futuristic sci-fi styling
- excessive neon
- glowing AI effects
- excessive glassmorphism
- artificial 3D farm graphics
- cartoon farming illustrations
- childish agricultural iconography

---

# 4. Green Theme — But Not a Generic Green Theme

Green is mandatory, but do not simply create a standard "green SaaS theme."

Green should represent **living crops and agriculture**.

Use a restrained palette built around:
- deep agricultural green
- leaf green
- muted olive
- soft field green
- warm off-white
- soil/brown neutrals
- natural dark text

Green should be the **identity color**, not the color of every component.

### Suggested visual hierarchy

- Deep green → primary navigation, major actions, active states
- Mid/leaf green → healthy crop states and positive agricultural indicators
- Olive → secondary agricultural information
- Warm cream/off-white → page surfaces
- Soil/warm neutral → occasional agricultural accents
- Red/orange/yellow → reserved for actual risk/severity states

Do not force all alerts to green simply because the product theme is green.

Risk colors must retain semantic meaning:

- Green = healthy / normal
- Yellow/amber = monitor
- Orange = attention
- Red = high risk / critical

---

# 5. Color Usage Rules

## DO

- Keep the overall interface light and natural.
- Use green as an anchor.
- Allow large areas of warm neutral background.
- Use color sparingly to establish hierarchy.
- Use risk colors only when their semantic meaning matters.

## DO NOT

- Make every card green.
- Use green gradients everywhere.
- Use green text on green backgrounds.
- Use five different shades of green in one component.
- Use red merely as a decorative accent.
- Use blue/purple as the dominant brand color.

---

# 6. Layout Philosophy

## 6.1 No "dashboard wall"

The home screen must not contain 15–20 KPI cards.

Instead, the home screen should have **three major visual priorities**:

### Priority 1 — Field situation

A large visual field/map area showing:
- field boundary
- zones
- current health
- problem areas
- rover position when active

### Priority 2 — What needs attention

A compact prioritized list containing only the most important:
- disease alerts
- pest alerts
- water-stress alerts
- environmental-risk alerts
- urgent recommendations

### Priority 3 — What is happening now

A compact live/activity area:
- rover status
- latest detection
- latest recommendation
- latest treatment event
- last scan

Everything else should be available through field detail, analytics, history, or drill-down.

---

# 7. Navigation Architecture

Use a **small number of meaningful destinations**.

Recommended primary navigation:

1. **Home**
2. **Fields**
3. **Live Rover**
4. **Insights**
5. **Alerts**

Avoid creating a separate top-level page for every backend entity.

For example, do NOT create:
- Diseases page
- Pests page
- Nutrients page
- Sensors page
- Zones page
- Spray page
- Irrigation page
- Weather page
- CNN page
- GPS page

These belong inside the relevant field context.

### Navigation principle

> **One field is the central unit of the application.**

The farmer enters a field and sees its complete story.

---

# 8. Home Screen

The Home screen is a **situational overview**, not an analytics warehouse.

## Required content

### Hero / contextual header

Use a strong agricultural visual or image composition near the top.

It may contain:
- crop imagery
- farmer + crop
- rover operating in a field
- aerial field pattern
- healthy crop landscape

The image must communicate a purpose.

Example:

**"Good morning. Here's what needs attention in your fields."**

The image should support the message rather than simply decorate the page.

### Main field overview

Show a small number of fields with:
- field name
- crop
- simple health status
- important issue
- last scan
- quick action

Do not show every metric here.

### Attention area

Example:

**Needs attention**

- Zone 5 — possible early blight
- Zone 8 — increasing pest activity
- North section — water stress
- Heat risk expected today

Each item should allow direct navigation to the relevant field/zone.

### Current rover activity

If a rover is active:
- scanning
- current field
- current zone
- latest detection
- connection state

If no rover is active, this section should remain quiet rather than showing an empty technical dashboard.

---

# 9. Field List

The Fields page should feel like a **farm overview**, not a database table.

Use visual field cards/list rows.

Each field should show:

- field name
- crop
- approximate area
- health status
- most important current issue
- last scan
- rover status if relevant
- quick "Open Field" action

Optional small visual:
- miniature map shape
- crop image
- simplified health preview

Do not show every available metric on the field card.

---

# 10. Field Detail — The Core Screen

The Field Detail screen is the most important screen in the application.

It should combine the field's **geography + health + activity + actions**.

Recommended structure:

```text
FIELD HEADER
    ↓
FIELD MAP / HEALTH MAP
    ↓
CURRENT SITUATION
    ↓
PRIORITY ACTIONS
    ↓
RECENT ACTIVITY
    ↓
TRENDS / HISTORY
```

Do not create separate pages for every one of these unless necessary.

---

# 11. Field Header

The header should immediately establish context.

Show:

- Field name
- Crop
- Area
- Current health status
- Last scan
- Active rover indicator
- Optional field image

Example:

**Tomato Field — North Plot**

`Moderate Health`

`Last scanned 10:51 AM`

The status should be visually obvious but not oversized.

---

# 12. The Field Map Is the Main Visual

The map is the application's primary spatial interface.

It should never feel like a generic map pasted into a dashboard.

The map should tell the story of the field.

## Map must support

- field boundary
- automatically generated zones
- rover current position
- rover route
- disease detections
- pest detections
- nutrient-deficiency detections
- water-stress areas
- environmental risk
- hotspots
- spray/treatment locations
- irrigation locations

These requirements are directly part of the software PRD.

## Map interaction

The farmer should be able to:

- zoom
- pan
- select a zone
- select a detection
- select rover
- toggle meaningful layers
- inspect hotspots
- inspect treated/untreated locations
- view rover route
- return to field extent

Do not display every layer simultaneously by default.

Use a compact layer control.

---

# 13. Map Layer Strategy

Default map state should be simple.

### Default

Show:
- field boundary
- zones
- current health/problem visualization
- rover position if active

### Optional layers

Available through a layer selector:

- Disease
- Pest
- Nutrient
- Water stress
- Environmental risk
- Hotspots
- Spray/treatment
- Irrigation
- Rover route

The farmer should be able to turn layers on/off.

Do not create a permanent row of 10 filter buttons.

---

# 14. Zones

Zones are generated by the software.

The farmer should not have to manually create zones in the MVP.

The UI should make the grid understandable without making it visually dominant.

Each zone should have:
- ID/name
- boundary
- area
- health state
- relevant problem
- prevalence
- trend
- risk
- treatment status
- last scan

Selecting a zone opens its detail context.

---

# 15. Do Not Color an Entire Zone From One Detection

A single detection should not visually imply that the entire zone is diseased.

The system should distinguish:

**Raw observation**

from

**Zone-level interpretation**

For example:

- One early-blight observation → individual detection marker
- Multiple detections → hotspot may develop
- High prevalence / concentration → zone risk increases

The visual system must preserve this distinction.

---

# 16. Hotspots

Hotspots should be visually meaningful.

Use:
- subtle density visualization
- heatmap
- cluster visualization
- affected-area emphasis

Do not use giant red circles everywhere.

The hotspot visual should communicate:

> "This is where the problem is concentrated."

The raw detections should remain accessible by clicking/drilling down.

---

# 17. Detection Detail

When a farmer selects a disease/pest/nutrient detection, show a focused detail panel or page.

Display:

- image/frame
- detected condition
- confidence
- timestamp
- geographic location
- field
- zone
- rover
- scan session
- severity/risk
- treatment status

The image is important here because it provides the evidence behind the detection.

The UI should clearly distinguish:

**Model observation**

from

**system recommendation**

Do not present a probabilistic CNN result as a confirmed diagnosis.

---

# 18. Image Usage Rules

Images are a core part of the visual identity, but images must **serve a purpose**.

## The user will provide 3 images

Create explicit placeholders for:

- `USER_IMAGE_01`
- `USER_IMAGE_02`
- `USER_IMAGE_03`

Claude must make these easy to replace without redesigning the layout.

## Claude may select additional images

Claude may independently choose suitable agricultural images when required.

Image selection should prioritize:
- Indian farming context where appropriate
- real farms
- real crops
- farmers
- field work
- crop inspection
- rover/farm technology
- irrigation
- crop health

Avoid generic corporate stock imagery where possible.

---

# 19. Image Storytelling Rule

Never place an image merely because "the page needs an image."

Every significant image must answer at least one question:

- What crop are we talking about?
- What farming activity is happening?
- What problem is being detected?
- What action is being taken?
- What does healthy agriculture look like?
- Where is the technology operating?

### Good

Large crop/farmer image next to a message:

**"Know what's happening in your field before the problem spreads."**

### Good

A rover image beside:

**"Rover scanning — Zone 5"**

### Good

A crop disease image inside detection details as evidence.

### Bad

A random farmer stock photo at the top of every page.

### Bad

A raw rectangular image with no relationship to the content.

---

# 20. Banner Rules

Use large banners selectively.

A banner should introduce:
- the product
- a farm/field context
- a major current situation
- an important seasonal/risk message
- a meaningful action

The supplied government agriculture website is a useful reference for this principle: its large imagery is integrated with agricultural messaging rather than appearing as isolated image blocks.

Do NOT reproduce that website's exact layout or styling.

Take only the underlying principle:

> **Agricultural imagery + meaningful message + clear navigation.**

---

# 21. Crop / Field Hero Areas

Hero sections can combine:

**Image + short message + contextual information + action**

Example:

```text
[large crop image]

TOMATO FIELD
North Plot

Moderate health
2 areas need attention

[View field]
```

Keep the text short.

Do not put paragraphs over photographs.

---

# 22. Farmer Advisory UI

Advisories are one of the most important parts of the product.

They must be written in plain, actionable language.

Every advisory should answer:

1. What is happening?
2. Where?
3. How serious?
4. What should I do?
5. Has action already been taken?

Example:

**Possible disease detected**

`Zone 5`

`Confidence: 93%`

**Action:** Inspect the affected area and treat if confirmed.

`Not yet treated`

Avoid technical wording such as:

> "CNN classification probability indicates a 0.93 posterior likelihood."

That belongs in technical detail, not the farmer-facing interface.

---

# 23. Alerts

Alerts should be prioritized rather than dumped into a notification center.

Examples:

- Possible disease detected
- Pest activity increasing
- High pest concentration in Zone 5
- Irrigate now
- Delay irrigation
- Heat-stress warning
- Flood-risk alert
- Drought-risk alert
- Possible nutrient deficiency

Each alert should show:
- severity
- what
- where
- time
- recommended action
- acknowledgement state

Avoid notification spam.

Repeated unchanged conditions should not generate endless duplicate alerts.

---

# 24. Risk Visualization

Use a consistent semantic hierarchy:

| State | Meaning |
|---|---|
| Healthy | No current significant issue |
| Monitor | Early / low concern |
| Attention | Action or inspection recommended |
| High Risk | Significant threat |
| Critical | Immediate attention |

The visual language should be understandable without requiring the farmer to interpret a chart.

---

# 25. Rover Live Screen

The Live Rover screen is an **operational mode**, not a standard analytics dashboard.

It should prioritize the map.

Suggested layout:

```text
LIVE ROVER

┌─────────────────────────────────────┐
│                                     │
│             FIELD MAP               │
│        rover + route + zones        │
│                                     │
└─────────────────────────────────────┘

ROVER #01   SCANNING
Zone 5      Connected

Latest observation
Early Blight · 93%

[View detection]
```

Optional supporting information:
- battery
- speed
- heading
- sensor values
- sprayer state
- connection status
- last update

Technical telemetry should remain secondary to the field view.

---

# 26. Rover Status

Use a compact status indicator.

Examples:

- Scanning
- Moving
- Idle
- Returning
- Spraying
- Offline
- Error

Do not create large industrial-machine UI unless the product later becomes an operations console.

---

# 27. Spraying / Treatment

The UI must distinguish four states:

**Detected → Recommended → Treated → Untreated**

This distinction is critical.

A detection does not mean spraying happened.

A recommendation does not mean spraying happened.

The interface must never imply successful treatment without a corresponding treatment event.

---

# 28. Treatment Visualization

On the field map:

- detection locations = observation
- recommendation locations = proposed action
- spray locations = actual treatment

Use different visual treatments for each.

Example conceptual legend:

```text
• Detection
○ Recommended treatment
▰ Treated area
× Untreated problem
```

Exact symbols may change during implementation, but semantic distinction must remain.

---

# 29. Irrigation

Irrigation should be presented as a decision.

Example:

**Water stress detected**

`South-east zone`

**Recommendation: Irrigate soon**

Supporting information may include:
- soil moisture
- temperature
- humidity
- rainfall
- forecast
- previous irrigation
- water usage

Do not show every sensor reading on the first layer.

Use progressive disclosure for technical values.

---

# 30. Environmental Risk

Environmental risks should be shown in a natural agricultural context.

Supported risks include:
- drought
- excessive rainfall
- flooding
- heat waves / heat stress
- disease-outbreak environmental conditions
- abnormal environmental patterns

Example:

**Heat risk — High**

`Expected high heat exposure today`

`Affected: Tomato Field`

`Action: Monitor crop stress and follow crop-specific advisory.`

---

# 31. Farm Analytics

Analytics are necessary, but should not dominate the home screen.

Create one **Insights** destination.

Possible sections within Insights:

### Crop Health
- crop-health trend
- disease detections
- pest detections
- nutrient deficiency trends
- water-stress trends

### Environment
- soil moisture
- temperature
- humidity
- rainfall/weather
- environmental risk

### Operations
- irrigation history
- treatment history
- zone comparisons

### Risk
- risk history
- yield-risk indicator
- treatment response

Use progressive disclosure.

---

# 32. Analytics Visualization Rules

Prefer:

- line charts for trends
- area charts for changing conditions where appropriate
- simple bars for comparisons
- map visualizations for spatial data
- compact numeric summaries for important values

Avoid:
- 3D charts
- donut-chart overload
- gauges everywhere
- decorative charts
- charts without decisions attached

Every chart should answer a useful question.

Examples:

**Disease detections over time**

> Is the problem increasing or decreasing?

**Soil moisture trend**

> Is the field becoming too dry?

**Treatment response**

> Did the observed problem improve after treatment?

---

# 33. Yield Risk

The interface must not claim an exact yield prediction unless the backend has a validated model and sufficient data.

Use:

**Yield Risk: Moderate**

rather than:

**Expected yield: 4.82 tonnes**

unless the actual prediction model supports that precision.

Show contributing factors:

- increasing disease
- pest pressure
- water stress
- heat stress
- environmental risk
- crop stage
- historical trend
- treatment response

---

# 34. Historical Treatment Effectiveness

When sufficient data exists, show:

**Treatment response**

- Improving
- Unchanged
- Worsening
- Insufficient data

Clearly label this as an observational metric.

Do not imply that the software has scientifically proven treatment causality.

---

# 35. Search and Filters

Do not permanently display a large filter panel.

Use a compact filter control with progressive disclosure.

Supported filters:

- field
- zone
- crop
- disease
- pest
- nutrient issue
- risk type
- date/time
- rover
- scan session
- treatment status
- alert severity

Filters should appear where they are relevant.

---

# 36. Tables

Tables should be used only when tabular comparison genuinely helps.

Examples:
- treatment history
- irrigation history
- scan history
- detection history
- equipment events

Do not convert every dataset into a table.

The default presentation should be visual/contextual.

---

# 37. Cards

Cards are allowed but must be used deliberately.

A card should represent a meaningful unit such as:
- a field
- an alert
- an advisory
- a detection
- a zone
- a recent event

Avoid cards inside cards inside cards.

Do not create a separate card for every number.

---

# 38. Component Density Rule

A screen should have:

**1 primary visual → 1 primary decision → a small number of supporting elements**

Not:

**20 components → 12 metrics → 8 charts → 5 filters → 3 sidebars**

If a screen feels crowded, move information behind:
- tabs
- expandable sections
- drawers
- detail views
- layer controls
- drill-down

Do not delete required functionality merely to make the UI cleaner.

---

# 39. Progressive Disclosure

The application should expose information in layers.

### Layer 1 — Farmer summary

"What is wrong and what should I do?"

### Layer 2 — Location

"Where exactly is the problem?"

### Layer 3 — Evidence

"What did the rover/camera/model observe?"

### Layer 4 — Technical detail

"GPS, timestamp, confidence, sensor values, model version, event data."

This allows the application to remain simple while still exposing complete system data.

---

# 40. Data Provenance Must Remain Visible in the Specification

When specifying UI data, document the source and format.

Use this notation:

<span style="color:gray">**Rover-populated data: field shown in UI — source: Raspberry Pi / AMB82-MINI / GPS / sensors / rover controller → backend; format: JSON.**</span>

For software-owned values:

<span style="color:gray">**Software data: field shown in UI — source: backend database/service; format: JSON API response / GeoJSON / relational entity as applicable.**</span>

For derived values:

<span style="color:gray">**Derived data: field shown in UI — source: backend analytics/geospatial/risk engine; format: specified UI value. Calculation: specified backend calculation. Raw data required: source observations/events required for calculation.**</span>

The frontend must never invent values that the backend does not provide.

---

# 41. Example Data Mapping

## Rover position

<span style="color:gray">**Rover-populated data: latitude, longitude, speed, heading, timestamp — source: GPS → Raspberry Pi → backend; format: JSON.**</span>

UI use:
- rover marker
- route
- current zone
- last update

## CNN detection

<span style="color:gray">**Rover-populated raw data: image/frame reference, CNN class, confidence, GPS, timestamp, rover_id — source: AMB82-MINI + CNN + GPS + Raspberry Pi; format: JSON event.**</span>

UI use:
- detection marker
- detection detail
- latest observation
- disease/pest analytics

## Field/zone association

<span style="color:gray">**Derived data: field_id and zone_id — source: backend geospatial engine; format: UUIDs. Calculation: point-in-polygon using detection GPS coordinate against stored field/zone polygons. Raw data required: latitude/longitude + field/zone polygons.**</span>

UI use:
- detection location
- zone detail
- field health
- hotspot calculations

## Treatment coverage

<span style="color:gray">**Derived data: treatment_coverage — source: backend geospatial analytics; format: percentage. Calculation: qualifying detected locations within treated coverage ÷ qualifying detected locations × 100. Raw data required: detection coordinates + treatment coordinates/coverage geometry + timestamps.**</span>

UI use:
- field treatment status
- treated vs untreated map
- treatment summary

---

# 42. Field Health Status

Every field needs one simple status.

Supported statuses:

- Healthy
- Monitor
- Attention required
- High risk
- Critical

The status should be derived from relevant field/zone risk metrics.

<span style="color:gray">**Derived data: field_risk_status — source: backend risk engine; format: categorical status + numeric score where applicable. Calculation: configured aggregation of active zone risks, disease/pest prevalence, water stress, and environmental risks. Raw data required: zone risk metrics + field environmental/sensor metrics.**</span>

The farmer should understand the status immediately without opening analytics.

---

# 43. Offline / Poor Connectivity UI

The application must acknowledge that farms may have intermittent connectivity.

Show a subtle connection state:

- Connected
- Syncing
- Offline
- Last synced X minutes ago

Do not make the entire UI look like an error state.

The edge detection pipeline should continue operating without continuous cloud connectivity.

<span style="color:gray">**Rover/edge data: queued events during connectivity loss — source: Raspberry Pi/edge device → local queue → backend synchronization; format: JSON events.**</span>

---

# 44. Empty States

Empty states should feel agricultural, not like developer tooling.

Example:

**No scans yet**

"Start a rover scan to begin building your field health map."

Optional supporting crop/field image.

Avoid:

`No data found.`

---

# 45. Loading States

Avoid generic skeleton overload.

Use meaningful loading messages when appropriate:

- "Loading your fields..."
- "Preparing field map..."
- "Syncing rover data..."
- "Loading latest observations..."

For live rover data, show last-known state while updating where safe.

---

# 46. Error States

Errors should explain:
- what happened
- whether data is still safe
- what the farmer can do

Example:

**Rover connection interrupted**

`Last update: 4 minutes ago`

"Scanning data collected on the rover will sync when the connection returns."

Avoid exposing stack traces or backend error codes to the farmer.

---

# 47. Typography

Typography should be:
- highly readable
- strong at headings
- comfortable at normal reading size
- suitable for rural/outdoor use

Avoid extremely thin fonts.

Use clear hierarchy:

**Large:** page/field title  
**Medium:** section title  
**Regular:** information  
**Small:** metadata / timestamps

Do not make important information tiny just to fit more content.

---

# 48. Icons

Use simple, recognizable icons.

Agricultural concepts may use:
- leaf
- field
- water
- droplet
- sun/heat
- rain
- insect
- crop
- rover
- location
- spray
- warning

Avoid icon overload.

Icons should reinforce text, not replace important text.

---

# 49. Map + Image Relationship

Use maps for:

**Where**

Use images for:

**What it looks like / evidence / human context**

Use charts for:

**How it is changing**

Use advisory cards for:

**What to do**

Use treatment history for:

**What was done**

This is a core visual grammar for the product.

---

# 50. Responsive Design

The product must work on:
- desktop
- tablet
- mobile

On smaller screens:

### Prioritize

1. current field status
2. alerts
3. map
4. latest detection
5. recommendation
6. rover status

Move advanced analytics behind tabs/sections.

Do not simply shrink the desktop dashboard onto mobile.

---

# 51. Accessibility / Outdoor Usability

Farmers may use the application:
- outdoors
- in bright light
- while moving around a field
- on mobile devices

Therefore:
- maintain strong contrast
- avoid tiny text
- use large touch targets
- don't communicate information by color alone
- provide text labels alongside icons
- keep actions obvious

---

# 52. Animation

Animation should be functional.

Good uses:
- rover moving on map
- live status update
- alert appearing
- map layer transition
- synchronization state

Avoid:
- animated gradients
- excessive page transitions
- floating decorative objects
- constant motion

The rover can have a subtle live-position indicator when active.

---

# 53. Design Language for Agricultural Technology

The application combines:

**Traditional visual context**
- fields
- crops
- farmers
- soil
- water
- natural textures

with

**Modern technology**
- maps
- live location
- AI detections
- analytics
- risk indicators
- connected rover

The combination should feel intentional.

The product should communicate:

> **Advanced technology operating in a real farm.**

Not:

> **A tech dashboard with a farming wallpaper.**

---

# 54. Avoid Clichés

Do not use:
- giant leaf logo everywhere
- cartoon farmer illustrations
- excessive green gradients
- generic "AI" glowing graphics
- stock photos on every section
- tractor clipart
- repeated plant icons
- "smart farming" buzzwords as decoration
- futuristic robot imagery unrelated to the actual rover
- generic dashboard templates

Authenticity should come from the actual workflow:
**field → rover → observation → location → risk → action → treatment.**

---

# 55. The User-Provided Three Images

Claude must support three user-provided images as first-class assets.

Create an asset configuration such as:

```text
USER_IMAGE_01
USER_IMAGE_02
USER_IMAGE_03
```

The implementation should make their placement configurable.

Suggested use:
- one hero/context image
- one field/crop story image
- one rover/farming activity image

However, Claude may change placement if the actual images make another placement more appropriate.

Do not crop or distort them arbitrarily.

---

# 56. Claude-Selected Images

Claude may add additional images where they materially improve the product.

For each selected image, Claude should ask:

1. What story does this image tell?
2. What section does it support?
3. Does it improve understanding?
4. Is it authentic to agriculture?
5. Is it necessary?

If the answer is no, do not add the image.

The implementation should ideally centralize image URLs/assets so they can be replaced later.

---

# 57. Recommended Home Visual Composition

A strong initial composition:

```text
┌─────────────────────────────────────────────────────────┐
│ Logo / Product                         Farmer / Profile │
├─────────────────────────────────────────────────────────┤
│ Home   Fields   Live Rover   Insights   Alerts          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Agricultural contextual image]                        │
│                                                         │
│  Your fields, at a glance                               │
│  2 areas need attention today                           │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  FIELD MAP / FIELD OVERVIEW                             │
│  boundary + zones + problems + rover                    │
│                                                         │
├───────────────────────────────┬─────────────────────────┤
│ NEEDS ATTENTION               │ LIVE / RECENT           │
│ • disease                     │ rover scanning           │
│ • pest                        │ latest detection         │
│ • water stress                │ latest action            │
│ • environmental risk          │ last sync                │
└───────────────────────────────┴─────────────────────────┘
```

This is a reference composition, not a rigid pixel-perfect requirement.

---

# 58. Recommended Field Screen Composition

```text
FIELD: TOMATO — NORTH PLOT
Moderate health · Last scan 10:51 AM

┌─────────────────────────────────────────────────────────┐
│                                                         │
│                    FIELD HEALTH MAP                    │
│                                                         │
│       zones + rover + detections + hotspots             │
│                                                         │
└─────────────────────────────────────────────────────────┘

[Health] [Problems] [Water] [Environment] [Treatment]

CURRENT SITUATION
Possible disease in Zone 5
Pest activity increasing in Zone 8

RECOMMENDED ACTION
Inspect Zone 5
Targeted treatment recommended in Zone 8

RECENT ACTIVITY
10:51  Rover scanned Zone 5
10:49  Early blight detected
10:47  Spray completed
```

Again: use progressive disclosure rather than placing all details simultaneously.

---

# 59. Functional Coverage Requirement

The visual simplification must NOT remove any required product functionality.

The UI must still provide access to:

### Crop Health
- visible disease detection
- nutrient deficiency detection
- crop growth-stage information
- overall field health

### Pest Detection
- common pest detection
- infestation patterns
- early warnings
- targeted intervention

### Irrigation
- soil moisture
- temperature
- humidity
- weather
- water stress
- over-irrigation
- irrigation recommendation
- irrigation events
- water-usage efficiency

### Environmental Risk
- drought
- excessive rainfall
- flooding
- heat stress
- disease-favorable environmental conditions
- abnormal environmental patterns
- localized alerts

### Edge AI
- on-device CNN processing
- low-latency detection
- intermittent connectivity
- queued synchronization

### Farmer Advisory
- what
- where
- severity
- recommended action
- action already taken

### Analytics
- disease trends
- pest trends
- nutrient trends
- water stress
- soil moisture
- temperature
- humidity
- rainfall/weather
- irrigation history
- treatment history
- zone comparisons
- risk history
- yield-risk indicator
- treatment response

### Spatial Intelligence
- field boundary
- automatic zones
- rover position
- rover route
- detections
- hotspots
- treatment locations
- irrigation locations

### Operations
- rover status
- camera/CNN activity
- spray status
- equipment integration
- scan sessions
- alerts
- recommendations
- historical records

---

# 60. Backend/UI Boundary

The frontend is responsible for:
- presentation
- interaction
- map rendering
- filtering
- drill-down
- visualization
- farmer-facing recommendations
- live state presentation

The backend is responsible for:
- authentication
- farm/field storage
- boundary storage
- zone generation
- geospatial processing
- edge ingestion
- detection storage
- field/zone mapping
- analytics
- hotspot calculation
- risk calculation
- recommendations
- alerts
- treatment tracking
- historical analytics
- synchronization

The UI must not recreate backend agricultural logic.

---

# 61. Core Data Flow the UI Represents

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
Determine Field
    ↓
Determine Zone
    ↓
Store Raw Observation
    ↓
Calculate Health / Risk / Hotspots
    ↓
Generate Advisory / Alert
    ↓
Farmer UI
    ↓
Targeted Treatment
    ↓
Spray / Irrigation Event
    ↓
Treatment History
    ↓
Historical Analytics
```

The UI should make this invisible complexity feel simple.

---

# 62. Information Architecture Rule

Do not expose the backend architecture directly.

The farmer should not need to understand:
- CNN models
- APIs
- event queues
- JSON
- geospatial engines
- UUIDs
- database entities

The farmer should see:
- field
- problem
- location
- severity
- action
- outcome

Technical details can exist behind "Details" or advanced views.

---

# 63. Final Design Test

Before considering any screen complete, ask:

### Question 1
Does this screen look like a farming application?

### Question 2
Is there one obvious primary purpose?

### Question 3
Can a farmer understand the most important information within a few seconds?

### Question 4
Are maps used for location and images used for context/evidence?

### Question 5
Have we avoided unnecessary cards, pages, charts, and controls?

### Question 6
Can the farmer reach the required functionality without the interface becoming cluttered?

### Question 7
Does every important alert lead to an actionable next step?

### Question 8
Does the UI distinguish observation, recommendation, and actual treatment?

### Question 9
Are images telling a story rather than acting as decoration?

### Question 10
Does the product feel like a real agricultural tool rather than a generic SaaS template?

If the answer to any of these is "no", redesign the screen.

---

# 64. Non-Negotiable Rules for Claude

1. **Do not build a generic admin dashboard.**
2. **Do not overpopulate the home screen.**
3. **Do not create a separate page for every feature/data entity.**
4. **Keep green as the brand identity, but do not make everything green.**
5. **Use real agricultural imagery purposefully.**
6. **The three user-provided images must be supported as configurable assets.**
7. **Claude may independently select additional images when they improve storytelling.**
8. **Do not use images as filler.**
9. **The field map is the primary spatial visual.**
10. **The field is the central product context.**
11. **Use progressive disclosure to expose the full functionality.**
12. **Do not remove required PRD functionality just to simplify the UI.**
13. **Do not present raw CNN probability as definitive diagnosis.**
14. **Do not imply spraying occurred unless a spray event exists.**
15. **Keep detected, recommended, treated, and untreated states distinct.**
16. **Do not invent sensor, GPS, spray, irrigation, or other hardware data.**
17. **Show data provenance in implementation specifications.**
18. **Use maps for WHERE, images for WHAT IT LOOKS LIKE, charts for HOW IT CHANGES, and advisories for WHAT TO DO.**
19. **Prefer one strong visual and one clear decision over many small components.**
20. **The final product must feel like technology built around a real farm, not a dashboard decorated with farming imagery.**

---

# 65. Reference to the Supplied Visual

The user-provided National Mission on Natural Farming screenshot should be treated as a **visual principle reference**, not a template.

What to take from it:

- strong agricultural identity
- large contextual imagery
- imagery integrated with messaging
- green agricultural navigation
- clear section hierarchy
- visual storytelling
- government/agricultural authenticity

What NOT to copy:

- exact navigation
- exact page structure
- exact colors
- exact cards
- exact typography
- exact banner treatment
- exact layout

The Smart Farming Assistant should be **more modern, more focused, less crowded, and more interactive**, while retaining the same principle of using agricultural visuals to establish context.

---

# 66. Product-Level Visual Goal

The final application should feel like:

> **A farmer's digital field companion.**

Not:

> **A dashboard containing agricultural data.**

The difference is fundamental.

The application can contain sophisticated AI, geospatial processing, telemetry, analytics, weather, irrigation, risk models, and treatment tracking underneath.

But the farmer-facing experience should remain:

**Field → See → Understand → Decide → Act → Track.**
