/* GrowForge — Settings */

const Settings = () => {
  const { Card, Badge, Btn } = window.GFC;
  const [tab, setTab] = React.useState("profile");

  return (
    <div data-screen-label="10 Settings">
      <div className="page-head">
        <div>
          <h1 className="page-title">Settings</h1>
          <div className="page-sub">Grow profile · units · rooms · alerts · data</div>
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "200px minmax(0, 1fr)", gap: 18 }}>
        <div className="card" style={{ height: "fit-content" }}>
          <div className="col" style={{ padding: 6 }}>
            {[
              ["profile","Grow profile","user"],
              ["units","Units","sort"],
              ["targets","Environment targets","trend"],
              ["rooms","Rooms & tents","rooms"],
              ["equipment","Equipment categories","equip"],
              ["stages","Growth stages","leaf"],
              ["notifications","Notifications","bell"],
              ["data","Data & exports","export"],
              ["theme","Theme","sun"],
              ["future","Future integrations","sensor"],
            ].map(([k, label, ic]) => (
              <button key={k} className={"nav-item " + (tab === k ? "active" : "")} onClick={() => setTab(k)} style={{ fontSize: 12.5 }}>
                <Icon name={ic} size={14}/>{label}
              </button>
            ))}
          </div>
        </div>

        <div className="col" style={{ gap: 18 }}>
          {tab === "profile" && <ProfileTab/>}
          {tab === "units" && <UnitsTab/>}
          {tab === "targets" && <TargetsTab/>}
          {tab === "rooms" && <RoomsTab/>}
          {tab === "equipment" && <EquipCatsTab/>}
          {tab === "stages" && <StagesTab/>}
          {tab === "notifications" && <NotifTab/>}
          {tab === "data" && <DataTab/>}
          {tab === "theme" && <ThemeTab/>}
          {tab === "future" && <FutureTab/>}
        </div>
      </div>
    </div>
  );
};

const Setting = ({ label, hint, control }) => (
  <div className="row" style={{ padding: "12px 0", borderBottom: "1px solid var(--line-soft)" }}>
    <div className="col">
      <span className="sm">{label}</span>
      {hint && <span className="dim tiny mono">{hint}</span>}
    </div>
    <div className="right" style={{ minWidth: 200, display:"flex", justifyContent:"flex-end" }}>{control}</div>
  </div>
);

const Toggle = ({ on = true }) => {
  const [v, set] = React.useState(on);
  return (
    <button onClick={() => set(!v)} style={{ width: 36, height: 20, borderRadius: 999, background: v ? "var(--accent)" : "var(--bg-3)", border: "1px solid var(--line-strong)", position:"relative", padding: 0 }}>
      <span style={{ position:"absolute", top: 2, left: v ? 18 : 2, width: 14, height: 14, borderRadius:"50%", background: v ? "var(--bg-0)" : "var(--fg-2)", transition:"left .15s" }}/>
    </button>
  );
};

const ProfileTab = () => {
  const { Card } = window.GFC;
  return (
    <Card title="Grow profile">
      <Setting label="Profile name" hint="Identifies this grow setup in reports" control={<input className="" defaultValue="Home tent — primary" style={{ background:"var(--bg-2)", border:"1px solid var(--line-strong)", borderRadius:6, padding:"6px 10px", color:"var(--fg-0)", width:240 }}/>}/>
      <Setting label="Mode" hint="Beginner shows tips; Advanced shows raw data" control={
        <div className="chips"><span className="chip">Beginner</span><span className="chip active">Advanced</span></div>
      }/>
      <Setting label="Time zone" control={<select style={{ background:"var(--bg-2)", border:"1px solid var(--line-strong)", borderRadius:6, padding:"6px 10px", color:"var(--fg-0)" }}><option>America/Los_Angeles · PDT</option><option>America/Denver · MDT</option></select>}/>
      <Setting label="Lights-on time" hint="Used to compute day/night metrics" control={<input defaultValue="09:00" style={{ width: 80, background:"var(--bg-2)", border:"1px solid var(--line-strong)", borderRadius:6, padding:"6px 10px", color:"var(--fg-0)" }}/>}/>
    </Card>
  );
};

const UnitsTab = () => {
  const { Card } = window.GFC;
  return (
    <Card title="Units">
      <Setting label="Temperature" control={<div className="chips"><span className="chip">°C</span><span className="chip active">°F</span></div>}/>
      <Setting label="Length / height" control={<div className="chips"><span className="chip">cm</span><span className="chip active">in</span></div>}/>
      <Setting label="Volume" control={<div className="chips"><span className="chip">L</span><span className="chip active">gal</span></div>}/>
      <Setting label="Mass" control={<div className="chips"><span className="chip">g</span><span className="chip active">oz</span></div>}/>
      <Setting label="Date format" control={<div className="chips"><span className="chip active">YYYY-MM-DD</span><span className="chip">MM/DD/YY</span></div>}/>
    </Card>
  );
};

const TargetsTab = () => {
  const { Card } = window.GFC;
  return (
    <Card title="Target environment ranges">
      <table className="tbl">
        <thead><tr><th>Stage</th><th>Temp °F</th><th>RH %</th><th>VPD kPa</th><th>Light hrs</th></tr></thead>
        <tbody>
          <tr><td>Seedling</td><td className="mono">70–78</td><td className="mono">65–75</td><td className="mono">0.6–0.9</td><td className="mono">18/6</td></tr>
          <tr><td>Vegetative</td><td className="mono">72–82</td><td className="mono">55–65</td><td className="mono">0.9–1.2</td><td className="mono">18/6</td></tr>
          <tr><td>Early flower</td><td className="mono">75–82</td><td className="mono">50–60</td><td className="mono">1.0–1.3</td><td className="mono">12/12</td></tr>
          <tr><td>Late flower</td><td className="mono">72–80</td><td className="mono">40–50</td><td className="mono">1.3–1.6</td><td className="mono">12/12</td></tr>
          <tr><td>Flushing</td><td className="mono">68–78</td><td className="mono">40–50</td><td className="mono">1.3–1.6</td><td className="mono">12/12</td></tr>
        </tbody>
      </table>
    </Card>
  );
};

const RoomsTab = () => {
  const { ROOMS } = window.GFData;
  const { Card, Btn, Badge } = window.GFC;
  return (
    <Card title="Rooms & tents" right={<Btn icon="plus" variant="ghost">Add room</Btn>}>
      <table className="tbl">
        <thead><tr><th>Name</th><th>Size</th><th>Stage assigned</th><th>Plants</th><th></th></tr></thead>
        <tbody>
          {ROOMS.map(r => (
            <tr key={r.id}>
              <td className="sm">{r.name}</td>
              <td className="mono dim">{r.id === "tent-flower" ? "5×5 ft" : r.id === "tent-veg" ? "4×4 ft" : "2×4 ft"}</td>
              <td><Badge tone="cool">{r.stage}</Badge></td>
              <td className="num mono">{r.plants}</td>
              <td><Icon name="more" size={14} className="ico"/></td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
};

const EquipCatsTab = () => {
  const { Card, Btn, Badge } = window.GFC;
  const cats = ["Lights","Inline Fan","Clip Fans","Humidifier","Dehumidifier","Heater","Sensors","Cameras","Controller","Tent","Nutrients","Misc Tools"];
  return (
    <Card title="Equipment categories" right={<Btn icon="plus" variant="ghost">Add category</Btn>}>
      <div className="chips">{cats.map(c => <span key={c} className="chip active">{c}</span>)}</div>
      <div className="dim tiny mono" style={{ marginTop: 10 }}>Categories are used to group equipment in lists and inform default UI affordances (icons, settings).</div>
    </Card>
  );
};

const StagesTab = () => {
  const { Card, Btn, Badge } = window.GFC;
  return (
    <Card title="Growth stage presets" right={<Btn icon="plus" variant="ghost">Add stage</Btn>}>
      <table className="tbl">
        <thead><tr><th>Stage</th><th>Default duration</th><th>Auto-reminders</th><th>Color</th></tr></thead>
        <tbody>
          <tr><td>Germination</td><td className="mono dim">3–7d</td><td className="dim">water check, first true leaves</td><td><Badge tone="violet" dot>violet</Badge></td></tr>
          <tr><td>Seedling</td><td className="mono dim">7–14d</td><td className="dim">watering schedule</td><td><Badge tone="ok" dot>green</Badge></td></tr>
          <tr><td>Vegetative</td><td className="mono dim">3–8w</td><td className="dim">veg nutrients, LST/topping</td><td><Badge tone="cool" dot>blue</Badge></td></tr>
          <tr><td>Flowering</td><td className="mono dim">7–12w</td><td className="dim">bloom nutrients, 12/12 confirm</td><td><Badge tone="warn" dot>amber</Badge></td></tr>
          <tr><td>Flushing</td><td className="mono dim">7–14d</td><td className="dim">plain water, trichome check</td><td><Badge tone="crit" dot>red</Badge></td></tr>
          <tr><td>Drying</td><td className="mono dim">10–14d</td><td className="dim">stem snap test</td><td><Badge tone="muted" dot>brown</Badge></td></tr>
          <tr><td>Curing</td><td className="mono dim">2–8w</td><td className="dim">jar burping, cure quality</td><td><Badge tone="muted" dot>slate</Badge></td></tr>
          <tr><td>Harvested</td><td className="mono dim">—</td><td className="dim">archive prompt</td><td><Badge tone="ok" dot>green</Badge></td></tr>
        </tbody>
      </table>
    </Card>
  );
};

const NotifTab = () => {
  const { Card } = window.GFC;
  return (
    <Card title="Notifications">
      <Setting label="In-app alerts" hint="Show alerts in the top-right bell" control={<Toggle on/>}/>
      <Setting label="Browser push" hint="Critical alerts only" control={<Toggle on/>}/>
      <Setting label="Email digest" hint="Daily morning summary" control={<Toggle on={false}/>}/>
      <Setting label="Quiet hours" hint="Suppress non-critical between 22:00 – 07:00" control={<Toggle on/>}/>
      <Setting label="Sound" hint="Audible chime for critical alerts" control={<Toggle on={false}/>}/>
    </Card>
  );
};

const DataTab = () => {
  const { Card, Btn } = window.GFC;
  return (
    <React.Fragment>
      <Card title="Data retention">
        <Setting label="Sensor history" hint="Older readings are downsampled to hourly averages" control={<select style={{ background:"var(--bg-2)", border:"1px solid var(--line-strong)", borderRadius:6, padding:"6px 10px", color:"var(--fg-0)" }}><option>90 days raw</option><option>180 days raw</option><option>365 days raw</option></select>}/>
        <Setting label="Photo retention" control={<select style={{ background:"var(--bg-2)", border:"1px solid var(--line-strong)", borderRadius:6, padding:"6px 10px", color:"var(--fg-0)" }}><option>Keep all</option><option>1 per week after harvest</option></select>}/>
        <Setting label="Auto-backup" hint="Local SQLite snapshot every 24h" control={<Toggle on/>}/>
      </Card>
      <Card title="Import / export">
        <div className="row" style={{ gap: 10, flexWrap: "wrap" }}>
          <Btn icon="export">Export full DB</Btn>
          <Btn icon="export">Export grow journal · PDF</Btn>
          <Btn icon="export">Export readings · CSV</Btn>
          <Btn icon="import">Import sensor CSV</Btn>
          <Btn icon="import">Restore from backup</Btn>
        </div>
        <div className="divider"/>
        <div className="dim tiny mono">Last backup: 2026-05-21 08:00 PDT · 2.3 MB · 14 tables</div>
      </Card>
    </React.Fragment>
  );
};

const ThemeTab = () => {
  const { Card } = window.GFC;
  return (
    <Card title="Theme">
      <Setting label="Color mode" control={<div className="chips"><span className="chip active">Dark</span><span className="chip">Light (planned)</span></div>}/>
      <Setting label="Accent" hint="Use the Tweaks panel to pick from 4 curated accents" control={<span className="dim tiny mono">→ open Tweaks</span>}/>
      <Setting label="Density" control={<div className="chips"><span className="chip">Compact</span><span className="chip active">Comfortable</span></div>}/>
      <Setting label="Mono font" control={<select style={{ background:"var(--bg-2)", border:"1px solid var(--line-strong)", borderRadius:6, padding:"6px 10px", color:"var(--fg-0)" }}><option>Geist Mono</option><option>JetBrains Mono</option><option>IBM Plex Mono</option></select>}/>
    </Card>
  );
};

const FutureTab = () => {
  const { Card, Badge } = window.GFC;
  return (
    <Card title="Future intelligence layer">
      <div className="dim sm" style={{ marginBottom: 12 }}>
        These features are planned for later releases. The current build is rule-based and manual — no AI or autonomous device control.
      </div>
      <div className="col" style={{ gap: 0 }}>
        <FutureRow label="Direct device control" desc="AC Infinity / Wyze / Govee integrations" eta="v1.1"/>
        <FutureRow label="Photo-based deficiency detection" desc="On-device image classifier" eta="v1.2"/>
        <FutureRow label="Pattern recognition for alerts" desc="Learns your grow's normal envelope" eta="v1.2"/>
        <FutureRow label="Predictive harvest scheduling" desc="Based on stage progression + strain" eta="v1.3"/>
        <FutureRow label="Strain comparison library" desc="Anonymized aggregate across grows" eta="v2.0"/>
      </div>
    </Card>
  );
};

const FutureRow = ({ label, desc, eta }) => (
  <div className="row" style={{ padding: "10px 0", borderBottom: "1px solid var(--line-soft)" }}>
    <div className="col">
      <span className="sm">{label}</span>
      <span className="dim tiny mono">{desc}</span>
    </div>
    <span className="right"><window.GFC.Badge tone="muted">{eta}</window.GFC.Badge></span>
  </div>
);

window.Settings = Settings;
