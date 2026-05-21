/* GrowForge — Sample data, realistic for an indoor grow */

const ROOMS = [
  { id: "tent-flower", name: "Flower Tent · 5x5", short: "Flower 5×5", stage: "Flowering", plants: 6, status: "ok", temp: 78.4, rh: 54, vpd: 1.34, light: "12/12", co2: 850 },
  { id: "tent-veg", name: "Veg Tent · 4x4", short: "Veg 4×4", stage: "Vegetative", plants: 5, status: "ok", temp: 75.1, rh: 62, vpd: 1.05, light: "18/6", co2: 720 },
  { id: "closet-mom", name: "Mother & Clone · 2x4", short: "Mom & Clone", stage: "Mother", plants: 8, status: "warn", temp: 74.2, rh: 71, vpd: 0.86, light: "18/6", co2: 600 },
];

const PLANTS = [
  { id: "p-01", name: "WC-1", strain: "Wedding Cake", type: "Photoperiod", stage: "Flowering", day: 47, room: "tent-flower", medium: "Living Soil", pot: "5 gal fabric", health: "ok", tags: ["flower","week 7"], lastWater: "12h ago", lastFeed: "3d ago", height: "78 cm" },
  { id: "p-02", name: "WC-2", strain: "Wedding Cake", type: "Photoperiod", stage: "Flowering", day: 47, room: "tent-flower", medium: "Living Soil", pot: "5 gal fabric", health: "ok", tags: ["flower","week 7"], lastWater: "12h ago", lastFeed: "3d ago", height: "82 cm" },
  { id: "p-03", name: "GG-1", strain: "Gorilla Glue #4", type: "Photoperiod", stage: "Flowering", day: 47, room: "tent-flower", medium: "Living Soil", pot: "5 gal fabric", health: "warn", tags: ["flower","week 7","watch"], lastWater: "11h ago", lastFeed: "3d ago", height: "71 cm", note: "Slight clawing on top fan leaves." },
  { id: "p-04", name: "GG-2", strain: "Gorilla Glue #4", type: "Photoperiod", stage: "Flowering", day: 47, room: "tent-flower", medium: "Living Soil", pot: "5 gal fabric", health: "ok", tags: ["flower","week 7"], lastWater: "12h ago", lastFeed: "3d ago", height: "74 cm" },
  { id: "p-05", name: "ZK-A", strain: "Zkittlez", type: "Photoperiod", stage: "Flowering", day: 47, room: "tent-flower", medium: "Living Soil", pot: "5 gal fabric", health: "ok", tags: ["flower","week 7"], lastWater: "12h ago", lastFeed: "3d ago", height: "65 cm" },
  { id: "p-06", name: "ZK-B", strain: "Zkittlez", type: "Photoperiod", stage: "Flowering", day: 47, room: "tent-flower", medium: "Living Soil", pot: "5 gal fabric", health: "ok", tags: ["flower","week 7"], lastWater: "12h ago", lastFeed: "3d ago", height: "67 cm" },
  { id: "p-07", name: "BD-V1", strain: "Blue Dream", type: "Photoperiod", stage: "Vegetative", day: 21, room: "tent-veg", medium: "Coco/Perlite", pot: "3 gal fabric", health: "ok", tags: ["veg","topped"], lastWater: "1d ago", lastFeed: "2d ago", height: "32 cm" },
  { id: "p-08", name: "BD-V2", strain: "Blue Dream", type: "Photoperiod", stage: "Vegetative", day: 21, room: "tent-veg", medium: "Coco/Perlite", pot: "3 gal fabric", health: "ok", tags: ["veg","topped"], lastWater: "1d ago", lastFeed: "2d ago", height: "30 cm" },
  { id: "p-09", name: "NL-V1", strain: "Northern Lights", type: "Autoflower", stage: "Vegetative", day: 18, room: "tent-veg", medium: "Coco/Perlite", pot: "3 gal fabric", health: "ok", tags: ["veg","auto"], lastWater: "1d ago", lastFeed: "2d ago", height: "26 cm" },
  { id: "p-10", name: "NL-V2", strain: "Northern Lights", type: "Autoflower", stage: "Seedling", day: 9, room: "tent-veg", medium: "Coco/Perlite", pot: "1 gal", health: "ok", tags: ["seedling"], lastWater: "8h ago", lastFeed: "—", height: "9 cm" },
  { id: "p-11", name: "GSC-V1", strain: "GSC", type: "Photoperiod", stage: "Vegetative", day: 28, room: "tent-veg", medium: "Living Soil", pot: "3 gal fabric", health: "ok", tags: ["veg","LST"], lastWater: "1d ago", lastFeed: "2d ago", height: "38 cm" },
  { id: "p-12", name: "M-WC", strain: "Wedding Cake", type: "Photoperiod", stage: "Mother", day: 142, room: "closet-mom", medium: "Coco/Perlite", pot: "5 gal fabric", health: "ok", tags: ["mother"], lastWater: "1d ago", lastFeed: "5d ago", height: "55 cm" },
  { id: "p-13", name: "M-GG", strain: "Gorilla Glue #4", type: "Photoperiod", stage: "Mother", day: 167, room: "closet-mom", medium: "Coco/Perlite", pot: "5 gal fabric", health: "ok", tags: ["mother"], lastWater: "1d ago", lastFeed: "5d ago", height: "58 cm" },
  { id: "p-14", name: "C-WC-04", strain: "Wedding Cake", type: "Clone", stage: "Rooting", day: 6, room: "closet-mom", medium: "Rapid Rooter", pot: "tray", health: "warn", tags: ["clone","rooting"], lastWater: "12h ago", lastFeed: "—", height: "—", note: "2/8 wilting, dome humidity low." },
];

const EQUIPMENT = [
  { id: "e-01", name: "Spider Farmer SE7000", cat: "Lights", room: "tent-flower", mode: "12/12 · 80% dim", status: "ok", lastSeen: "2 min ago", power: "536 W", note: "Cycle: lights-on at 09:00" },
  { id: "e-02", name: "Spider Farmer SE4500", cat: "Lights", room: "tent-veg", mode: "18/6 · 65%", status: "ok", lastSeen: "2 min ago", power: "211 W", note: "Cycle: lights-on at 06:00" },
  { id: "e-03", name: "AC Infinity Cloudline T6", cat: "Inline Fan", room: "tent-flower", mode: "Auto · Speed 5/10", status: "ok", lastSeen: "1 min ago", power: "32 W", note: "Trigger: RH > 60% or temp > 80°F" },
  { id: "e-04", name: "AC Infinity Cloudline T4", cat: "Inline Fan", room: "tent-veg", mode: "Auto · Speed 4/10", status: "ok", lastSeen: "1 min ago", power: "16 W" },
  { id: "e-05", name: "AC Infinity Cloudray 6\"", cat: "Clip Fans", room: "tent-flower", mode: "Manual · 40%", status: "ok", lastSeen: "—" },
  { id: "e-06", name: "AC Infinity Cloudray 6\" (×2)", cat: "Clip Fans", room: "tent-veg", mode: "Manual · 30%", status: "ok", lastSeen: "—" },
  { id: "e-07", name: "Levoit Classic 300S", cat: "Humidifier", room: "closet-mom", mode: "Target 70% RH", status: "warn", lastSeen: "8 min ago", note: "Reservoir at 14% — refill due." },
  { id: "e-08", name: "Inkbird Dehumidifier 35-pt", cat: "Dehumidifier", room: "tent-flower", mode: "Auto · 55% target", status: "ok", lastSeen: "3 min ago", power: "210 W" },
  { id: "e-09", name: "Lasko Ceramic Heater", cat: "Heater", room: "—", mode: "Standby (off)", status: "off", lastSeen: "—" },
  { id: "e-10", name: "Govee H5179 Sensor", cat: "Sensors", room: "tent-flower", mode: "BLE · 60s interval", status: "ok", lastSeen: "32 sec ago", note: "Battery: 78%" },
  { id: "e-11", name: "Govee H5179 Sensor", cat: "Sensors", room: "tent-veg", mode: "BLE · 60s interval", status: "ok", lastSeen: "32 sec ago", note: "Battery: 84%" },
  { id: "e-12", name: "Govee H5179 Sensor", cat: "Sensors", room: "closet-mom", mode: "BLE · 60s interval", status: "crit", lastSeen: "47 min ago", note: "Offline — last reading stale." },
  { id: "e-13", name: "Wyze Cam v3 (×2)", cat: "Cameras", room: "tent-flower", mode: "24/7 record", status: "ok", lastSeen: "now" },
  { id: "e-14", name: "AC Infinity Controller 69 Pro", cat: "Controller", room: "tent-flower", mode: "Auto envelope", status: "ok", lastSeen: "now", note: "Firmware 3.4.2" },
  { id: "e-15", name: "Mars Hydro 5×5 tent", cat: "Tent", room: "tent-flower", mode: "—", status: "ok", lastSeen: "—" },
  { id: "e-16", name: "Vivosun 4×4 tent", cat: "Tent", room: "tent-veg", mode: "—", status: "ok", lastSeen: "—" },
  { id: "e-17", name: "Gaia Green 4-4-4", cat: "Nutrients", room: "—", mode: "Top dress · 2 tbsp / gal", status: "ok", lastSeen: "—", note: "23% of bag remaining" },
  { id: "e-18", name: "Recharge microbes", cat: "Nutrients", room: "—", mode: "1 tsp / gal weekly", status: "ok", lastSeen: "—" },
  { id: "e-19", name: "pH/EC Pen — Apera AI209", cat: "Misc Tools", room: "—", mode: "—", status: "warn", lastSeen: "—", note: "Calibration due — 23 days since last." },
];

const TASKS = [
  { id: "t-01", title: "Water flower tent (round 1)", due: "Today · 18:00", priority: "high", room: "tent-flower", related: "All flower plants", done: false, recurring: "every 2d" },
  { id: "t-02", title: "Top-dress with Gaia Green 4-4-4", due: "Today · 19:00", priority: "med", room: "tent-flower", related: "WC-1, WC-2, GG-1, GG-2", done: false, recurring: "weekly" },
  { id: "t-03", title: "Refill Levoit 300S reservoir", due: "Today · 22:00", priority: "high", room: "closet-mom", related: "Levoit 300S", done: false },
  { id: "t-04", title: "Inspect clone dome — 2 wilting", due: "Today · 21:00", priority: "high", room: "closet-mom", related: "C-WC-04", done: false },
  { id: "t-05", title: "Take weekly progress photos", due: "Tomorrow · 09:00", priority: "low", room: "tent-flower", related: "All flower plants", done: false, recurring: "weekly" },
  { id: "t-06", title: "Calibrate pH pen (Apera)", due: "Tomorrow · 12:00", priority: "med", room: "—", related: "pH/EC Pen", done: false },
  { id: "t-07", title: "Defoliate lower canopy", due: "Sat · 11:00", priority: "med", room: "tent-flower", related: "WC-1, WC-2", done: false },
  { id: "t-08", title: "Inspect leaves for thrips", due: "Sun · 10:00", priority: "low", room: "tent-veg", related: "All veg plants", done: false, recurring: "weekly" },
  { id: "t-09", title: "Clean fan intake screens", due: "Mon · 19:00", priority: "low", room: "tent-flower", related: "Cloudline T6", done: false, recurring: "monthly" },
  { id: "t-10", title: "Water veg tent (round 2)", due: "Yesterday · 18:00", priority: "high", room: "tent-veg", related: "All veg plants", done: true },
  { id: "t-11", title: "Adjust SE7000 height +5cm", due: "Tue · 09:00", priority: "low", room: "tent-flower", related: "SE7000", done: true },
];

const ALERTS = [
  { id: "a-01", sev: "warn", title: "Humidifier reservoir low", source: "Levoit 300S · Closet", time: "8 min ago", state: "open", suggest: "Refill within 2 hours to avoid RH drop below 55%.", related: "closet-mom" },
  { id: "a-02", sev: "crit", title: "Sensor offline — 47 min", source: "Govee · Closet", time: "47 min ago", state: "open", suggest: "Check BLE bridge or replace battery (last reported 12%).", related: "closet-mom" },
  { id: "a-03", sev: "warn", title: "RH high in clone dome", source: "Closet · 71% RH", time: "1h ago", state: "ack", suggest: "Vent dome 30s; reduce humidifier set-point to 65%.", related: "closet-mom" },
  { id: "a-04", sev: "info", title: "Stage change due", source: "BD-V1 · 21 days in veg", time: "3h ago", state: "open", suggest: "Consider flip to 12/12 next 5–7 days.", related: "p-07" },
  { id: "a-05", sev: "warn", title: "Calibration overdue", source: "Apera AI209 · 23 days", time: "today", state: "open", suggest: "Calibrate with pH 4.01 and 7.00 buffer.", related: "e-19" },
  { id: "a-06", sev: "ok", title: "VPD entered ideal zone", source: "Flower tent · 1.34 kPa", time: "yesterday", state: "resolved", suggest: "—", related: "tent-flower" },
  { id: "a-07", sev: "warn", title: "Temp spike — 84°F peak", source: "Flower tent", time: "2 days ago", state: "resolved", suggest: "Inline fan ramped to 8/10, recovered in 18 min.", related: "tent-flower" },
];

const LOG = [
  { id: "l-01", t: "Today · 18:14", type: "Watering", plant: "WC-1, WC-2, GG-1, GG-2, ZK-A, ZK-B", room: "tent-flower", author: "you", note: "Plain RO water, 1 gal / plant. Runoff pH 6.4, EC 1.1.", ph: 6.4, ec: 1.1, water: 3785 },
  { id: "l-02", t: "Today · 18:00", type: "Observation", plant: "GG-1", room: "tent-flower", author: "you", note: "Mild clawing on top fan leaves. Watching, not adjusting yet.", tags: ["watch"] },
  { id: "l-03", t: "Today · 09:42", type: "Photo", plant: "WC-1", room: "tent-flower", author: "you", note: "Weekly progress photo (week 7 of flower).", hasPhoto: true },
  { id: "l-04", t: "Today · 09:30", type: "Environment", plant: "—", room: "tent-flower", author: "system", note: "Lights on. VPD entered ideal zone at 1.34 kPa." },
  { id: "l-05", t: "Yesterday · 21:10", type: "Training", plant: "GSC-V1", room: "tent-veg", author: "you", note: "LST — pulled two side branches down with soft ties." },
  { id: "l-06", t: "Yesterday · 19:00", type: "Feeding", plant: "BD-V1, BD-V2, NL-V1, GSC-V1", room: "tent-veg", author: "you", note: "Half-strength Recharge top-dress + plain water.", ec: 0.8 },
  { id: "l-07", t: "2 days ago · 11:20", type: "Pruning", plant: "WC-1, WC-2", room: "tent-flower", author: "you", note: "Light defoliation, removed lower fan leaves blocking under-canopy bud sites." },
  { id: "l-08", t: "2 days ago · 09:05", type: "Equipment", plant: "—", room: "tent-flower", author: "you", note: "Raised SE7000 light by 5cm; previous distance was 35cm." },
  { id: "l-09", t: "3 days ago · 18:30", type: "Watering", plant: "All veg", room: "tent-veg", author: "you", note: "Plain water, 0.75 gal / plant. Runoff pH 6.5, EC 0.9.", ph: 6.5, ec: 0.9, water: 2839 },
  { id: "l-10", t: "4 days ago · 14:00", type: "Pest Treatment", plant: "M-WC", room: "closet-mom", author: "you", note: "Spotted 1 fungus gnat — sprinkled mosquito bits on top of soil." },
  { id: "l-11", t: "5 days ago · 10:00", type: "Stage Change", plant: "NL-V2", room: "tent-veg", author: "you", note: "Moved from germination → seedling after first true leaves." },
  { id: "l-12", t: "6 days ago · 09:00", type: "Clone Taken", plant: "M-WC", room: "closet-mom", author: "you", note: "Took 8 cuts from M-WC for batch C-WC-04, rooting gel + Rapid Rooter." },
];

/* Time-series data — current week of readings (24 buckets, hourly) */
function genSeries(seed, base, amp, period = 24, phase = 0) {
  let r = seed;
  const out = [];
  for (let i = 0; i < period; i++) {
    r = (r * 9301 + 49297) % 233280;
    const noise = (r / 233280 - 0.5) * amp * 0.4;
    const wave = Math.sin((i / period) * Math.PI * 2 + phase) * amp;
    out.push(+(base + wave + noise).toFixed(2));
  }
  return out;
}

const SERIES = {
  tempF: genSeries(11, 77.5, 2.6, 24),
  rh: genSeries(23, 55, 6, 24, 1.2),
  vpd: genSeries(31, 1.32, 0.22, 24, 0.3),
  co2: genSeries(7, 820, 90, 24, 0.6),
  tempF_7d: genSeries(15, 77, 3, 168, 0.0),
  rh_7d: genSeries(27, 56, 8, 168, 0.8),
  vpd_7d: genSeries(33, 1.3, 0.25, 168, 0.4),
};

window.GFData = { ROOMS, PLANTS, EQUIPMENT, TASKS, ALERTS, LOG, SERIES };
