/* GrowForge — App shell, routing, sidebar, topbar, mobile nav */

const { useState, useEffect } = React;
const { Btn, BrandMark } = window.GFC;

const NAV = [
  { key: "dashboard", label: "Dashboard", icon: "dashboard" },
  { key: "environment", label: "Environment", icon: "env" },
  { key: "plants", label: "Plants", icon: "plants", count: window.GFData.PLANTS.length },
  { key: "growlog", label: "Grow Log", icon: "log", count: window.GFData.LOG.length },
  { key: "equipment", label: "Equipment", icon: "equip", count: window.GFData.EQUIPMENT.length },
  { key: "tasks", label: "Tasks", icon: "tasks", count: window.GFData.TASKS.filter(t => !t.done).length, alert: true },
  { key: "rooms", label: "Rooms", icon: "rooms", count: window.GFData.ROOMS.length },
  { key: "alerts", label: "Alerts", icon: "alerts", count: window.GFData.ALERTS.filter(a => a.state !== "resolved").length, alert: true },
  { key: "reports", label: "Reports", icon: "reports" },
  { key: "settings", label: "Settings", icon: "settings" },
];

const TWEAKS_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "sage",
  "density": "comfortable",
  "showHelp": true
}/*EDITMODE-END*/;

const ACCENT_HUES = { sage: 145, blue: 230, amber: 75, violet: 305 };

function App() {
  const [page, setPage] = useState("dashboard");
  const [plantId, setPlantId] = useState(null);
  const [room, setRoomVal] = useState("tent-flower");
  const [modal, setModal] = useState(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [tweaks, setTweak] = (window.useTweaks ? window.useTweaks(TWEAKS_DEFAULTS) : [TWEAKS_DEFAULTS, () => {}]);

  // Apply accent hue
  useEffect(() => {
    const hue = ACCENT_HUES[tweaks.accent] || 145;
    document.documentElement.style.setProperty("--accent-hue", hue);
  }, [tweaks.accent]);

  const go = (key, id) => {
    setPage(key);
    if (key === "plant-detail") setPlantId(id);
    window.scrollTo({ top: 0, behavior: "instant" });
  };
  const setRoom = (r) => setRoomVal(r);

  // Render page
  let body = null;
  if (page === "dashboard") body = <window.Dashboard room={room} go={go} openModal={setModal}/>;
  else if (page === "environment") body = <window.Environment room={room}/>;
  else if (page === "plants") body = <window.Plants go={go} openModal={setModal} room={room}/>;
  else if (page === "plant-detail") body = <window.PlantDetail plantId={plantId} go={go}/>;
  else if (page === "growlog") body = <window.GrowLog openModal={setModal}/>;
  else if (page === "equipment") body = <window.Equipment openModal={setModal}/>;
  else if (page === "tasks") body = <window.Tasks openModal={setModal}/>;
  else if (page === "rooms") body = <window.Rooms go={go} setRoom={setRoom}/>;
  else if (page === "alerts") body = <window.Alerts/>;
  else if (page === "reports") body = <window.Reports/>;
  else if (page === "settings") body = <window.Settings/>;

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><BrandMark/></div>
          <div className="brand-text">
            <span className="name">GrowForge</span>
            <span className="ver">v1.0.0 · command center</span>
          </div>
        </div>

        <div className="nav-section">
          <div className="nav-label">Operate</div>
          {NAV.slice(0, 8).map(n => (
            <button key={n.key} className={"nav-item " + (page === n.key || (page === "plant-detail" && n.key === "plants") ? "active" : "")} onClick={() => go(n.key)}>
              <Icon name={n.icon}/>
              {n.label}
              {n.count != null && <span className={"count " + (n.alert && n.count > 0 ? "alert" : "")}>{n.count}</span>}
            </button>
          ))}
        </div>

        <div className="nav-section">
          <div className="nav-label">Analyze</div>
          {NAV.slice(8).map(n => (
            <button key={n.key} className={"nav-item " + (page === n.key ? "active" : "")} onClick={() => go(n.key)}>
              <Icon name={n.icon}/>
              {n.label}
            </button>
          ))}
        </div>

        <div className="sidebar-foot">
          <div className="sysbar">
            <span className="dot"/>
            <span className="label">System healthy</span>
            <span className="meta">32s</span>
          </div>
          <div className="row" style={{ marginTop: 8, padding: "4px 6px" }}>
            <span style={{ width: 24, height: 24, borderRadius: "50%", background: "linear-gradient(135deg, oklch(0.5 0.08 145), oklch(0.35 0.06 145))", display:"grid", placeItems:"center", color:"#0a0d0c", fontSize: 11, fontWeight: 600 }}>JD</span>
            <span className="sm">jordan</span>
            <span className="dim tiny mono right">PDT</span>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="main">
        {/* Topbar */}
        <div className="topbar">
          <button className="btn btn-icon mobile-only" onClick={() => setSearchOpen(s => !s)} aria-label="Menu"><Icon name="menu" size={16}/></button>
          <div className="crumbs hide-on-mobile">
            <span style={{ color: "var(--fg-3)" }}>GrowForge</span>
            <span className="sep">/</span>
            <span className="now">{NAV.find(n => n.key === page)?.label || (page === "plant-detail" ? "Plant detail" : "—")}</span>
          </div>

          <div className="room-pill hide-on-mobile">
            <span className="dot"/>
            <span className="label">Room</span>
            <select value={room} onChange={e => setRoom(e.target.value)}>
              {window.GFData.ROOMS.map(r => <option key={r.id} value={r.id}>{r.short}</option>)}
            </select>
          </div>

          <div className="search hide-on-mobile">
            <Icon name="search" size={13}/>
            <input placeholder="Search plants, logs, equipment, tasks…"/>
            <span className="kbd">⌘ K</span>
          </div>

          <div className="top-actions">
            <Btn icon="plus" onClick={() => setModal("log")} title="Add log entry">Log</Btn>
            <Btn icon="plus" onClick={() => setModal("task")} title="Add task">Task</Btn>
            <button className="btn btn-icon" title="Notifications" style={{ position: "relative" }}>
              <Icon name="bell" size={14}/>
              <span style={{ position:"absolute", top: 4, right: 4, width: 6, height: 6, borderRadius:"50%", background:"var(--warn)" }}/>
            </button>
            <button className="btn btn-icon" title="Account" style={{ background: "linear-gradient(135deg, oklch(0.5 0.08 145), oklch(0.35 0.06 145))", color:"#0a0d0c", fontWeight: 600, fontSize: 11 }}>JD</button>
          </div>
        </div>

        <div className="page">
          {body}
        </div>

        {/* Mobile bottom nav */}
        <nav className="bnav">
          {[
            { key: "dashboard", label: "Home", icon: "dashboard" },
            { key: "environment", label: "Env", icon: "env" },
            { key: "plants", label: "Plants", icon: "plants" },
            { key: "tasks", label: "Tasks", icon: "tasks" },
            { key: "alerts", label: "Alerts", icon: "alerts" },
          ].map(n => (
            <button key={n.key} className={"bni " + (page === n.key ? "active" : "")} onClick={() => go(n.key)}>
              <Icon name={n.icon} size={18}/>
              <span>{n.label}</span>
            </button>
          ))}
        </nav>
      </main>

      {modal && <window.GFModal kind={modal} onClose={() => setModal(null)}/>}

      {/* Tweaks panel */}
      {window.TweaksPanel && (
        <window.TweaksPanel title="Tweaks">
          <window.TweakSection label="Brand accent">
            <window.TweakRadio label="Hue" value={tweaks.accent} onChange={v => setTweak("accent", v)} options={[
              { value: "sage", label: "Sage" },
              { value: "blue", label: "Cool" },
              { value: "amber", label: "Amber" },
              { value: "violet", label: "Violet" },
            ]}/>
          </window.TweakSection>
          <window.TweakSection label="Layout">
            <window.TweakRadio label="Density" value={tweaks.density} onChange={v => setTweak("density", v)} options={[
              { value: "compact", label: "Compact" },
              { value: "comfortable", label: "Comfy" },
            ]}/>
            <window.TweakToggle label="Roadmap callouts" value={tweaks.showHelp} onChange={v => setTweak("showHelp", v)}/>
          </window.TweakSection>
        </window.TweaksPanel>
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
