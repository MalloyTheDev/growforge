/* GrowForge — Equipment */

const Equipment = ({ openModal }) => {
  const { EQUIPMENT, ROOMS } = window.GFData;
  const { Card, Badge, Btn, StatusRow } = window.GFC;
  const cats = ["All","Lights","Inline Fan","Clip Fans","Humidifier","Dehumidifier","Heater","Sensors","Cameras","Controller","Tent","Nutrients","Misc Tools"];
  const [cat, setCat] = React.useState("All");
  const [active, setActive] = React.useState(null);

  const list = EQUIPMENT.filter(e => cat === "All" || e.cat === cat);
  const grouped = list.reduce((acc, e) => { (acc[e.cat] = acc[e.cat] || []).push(e); return acc; }, {});

  return (
    <div data-screen-label="05 Equipment">
      <div className="page-head">
        <div>
          <h1 className="page-title">Equipment</h1>
          <div className="page-sub">{EQUIPMENT.length} items · {EQUIPMENT.filter(e=>e.status==="ok").length} online · {EQUIPMENT.filter(e=>e.status==="warn"||e.status==="crit").length} need attention</div>
        </div>
        <div className="row">
          <Btn icon="filter">Filter</Btn>
          <Btn variant="primary" icon="plus" onClick={() => openModal("equipment")}>Add equipment</Btn>
        </div>
      </div>

      <div className="row" style={{ marginBottom: 14, gap: 8, flexWrap:"wrap" }}>
        {cats.map(c => <span key={c} className={"chip " + (cat === c ? "active" : "")} onClick={() => setCat(c)}>{c}</span>)}
      </div>

      <div className="col" style={{ gap: 24 }}>
        {Object.entries(grouped).map(([cn, items]) => (
          <div key={cn}>
            <div className="row" style={{ marginBottom: 10, gap: 8 }}>
              <Icon name={catIcon(cn)} size={14} className="ico"/>
              <span className="mono" style={{ fontSize: 13, color: "var(--fg-1)" }}>{cn}</span>
              <span className="dim tiny mono right">{items.length} · {items.filter(i=>i.status==="ok").length} ok</span>
            </div>
            <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))" }}>
              {items.map(e => <EquipCard key={e.id} item={e} onClick={() => setActive(e)}/>)}
            </div>
          </div>
        ))}
      </div>

      {/* Integration banner */}
      <div className="card" style={{ marginTop: 24, borderStyle:"dashed" }}>
        <div className="card-pad row" style={{ gap: 12, padding: "12px 16px" }}>
          <Icon name="info" size={14} className="ico" />
          <div className="col">
            <span className="sm">Direct device control: <Badge tone="muted">integration pending</Badge></span>
            <span className="dim tiny mono">Current build supports manual tracking. Hardware control (AC Infinity, Govee, Wyze) is roadmapped — readings are logged manually or via CSV import.</span>
          </div>
        </div>
      </div>

      {active && <EquipDrawer item={active} onClose={() => setActive(null)}/>}
    </div>
  );
};

function catIcon(c) {
  return c === "Lights" ? "bulb" :
         c === "Inline Fan" || c === "Clip Fans" ? "fan" :
         c === "Humidifier" || c === "Dehumidifier" ? "drop" :
         c === "Heater" ? "thermo" :
         c === "Sensors" ? "sensor" :
         c === "Cameras" ? "cam" :
         c === "Controller" ? "settings" :
         c === "Tent" ? "rooms" :
         c === "Nutrients" ? "leaf" : "wrench";
}

const EquipCard = ({ item, onClick }) => {
  const { ROOMS } = window.GFData;
  const { Badge } = window.GFC;
  const r = ROOMS.find(x => x.id === item.room);
  return (
    <div className="card" onClick={onClick} style={{ cursor:"pointer", transition: "border-color .12s" }}
         onMouseEnter={e => e.currentTarget.style.borderColor = "var(--accent-line)"}
         onMouseLeave={e => e.currentTarget.style.borderColor = "var(--line)"}>
      <div className="card-pad">
        <div className="row" style={{ gap: 10, marginBottom: 8 }}>
          <span style={{ width: 32, height: 32, borderRadius: 6, background: "var(--bg-2)", display:"grid", placeItems:"center", color:"var(--fg-2)" }}>
            <Icon name={catIcon(item.cat)} size={16}/>
          </span>
          <div className="col" style={{ flex:1, minWidth:0 }}>
            <div className="sm" style={{ overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{item.name}</div>
            <div className="dim tiny mono">{item.cat}</div>
          </div>
          <span className={"s-dot " + (item.status === "ok" ? "ok" : item.status === "warn" ? "warn" : item.status === "crit" ? "crit" : "off")}/>
        </div>
        <div className="kv"><span className="k">Mode</span><span className="v">{item.mode || "—"}</span></div>
        <div className="kv"><span className="k">Room</span><span className="v">{r?.short || "—"}</span></div>
        <div className="kv"><span className="k">Last seen</span><span className="v">{item.lastSeen || "—"}</span></div>
        {item.power && <div className="kv"><span className="k">Power</span><span className="v">{item.power}</span></div>}
        {item.note && <div className="tiny dim" style={{ marginTop: 8, padding: 8, background:"var(--bg-2)", borderRadius: 4, borderLeft: `2px solid ${item.status === "warn" ? "var(--warn)" : item.status === "crit" ? "var(--crit)" : "var(--accent)"}` }}>{item.note}</div>}
      </div>
    </div>
  );
};

const EquipDrawer = ({ item, onClose }) => {
  const { ROOMS } = window.GFData;
  const { Card, Badge, Btn } = window.GFC;
  const r = ROOMS.find(x => x.id === item.room);
  return (
    <React.Fragment>
      <div className="scrim" onClick={onClose}/>
      <div className="drawer">
        <div className="drawer-head">
          <Icon name={catIcon(item.cat)} size={18}/>
          <div className="col">
            <h2>{item.name}</h2>
            <span className="dim tiny mono">{item.cat} · {r?.short || "—"}</span>
          </div>
          <span className="right"><Btn icon="x" variant="ghost" onClick={onClose}/></span>
        </div>
        <div className="drawer-body">
          <div className="row" style={{ marginBottom: 14, gap: 8 }}>
            <Badge tone={item.status === "ok" ? "ok" : item.status === "warn" ? "warn" : item.status === "crit" ? "crit" : "muted"} dot>{item.status === "off" ? "Offline" : item.status}</Badge>
            <span className="dim tiny mono">Last seen {item.lastSeen}</span>
          </div>

          <SectionBlock title="Configuration">
            <div className="col">
              <div className="kv"><span className="k">Mode</span><span className="v">{item.mode || "—"}</span></div>
              <div className="kv"><span className="k">Assigned room</span><span className="v">{r?.name || "—"}</span></div>
              <div className="kv"><span className="k">Power draw</span><span className="v">{item.power || "—"}</span></div>
              <div className="kv"><span className="k">Connection</span><span className="v">{item.cat === "Sensors" ? "BLE" : item.cat === "Cameras" ? "Wi-Fi" : "Manual"}</span></div>
            </div>
          </SectionBlock>

          <SectionBlock title="Manual override" hint="Direct control not wired yet — log changes here.">
            <div className="grid" style={{ gridTemplateColumns:"1fr 1fr", gap: 8 }}>
              <Btn icon="play">Turn on</Btn>
              <Btn icon="pause">Turn off</Btn>
              <Btn icon="trend">Increase</Btn>
              <Btn icon="trend">Decrease</Btn>
            </div>
            <div className="tiny dim mono" style={{ marginTop: 8 }}>All actions create an Equipment log entry.</div>
          </SectionBlock>

          <SectionBlock title="Maintenance">
            <div className="col" style={{ gap: 8 }}>
              <MaintRow date="3 days ago" what="Cleaned intake screen"/>
              <MaintRow date="2 weeks ago" what="Firmware updated to 3.4.2"/>
              <MaintRow date="6 weeks ago" what="Installed initial"/>
            </div>
            <Btn icon="plus" variant="ghost" style={{ marginTop: 8 }}>Add maintenance entry</Btn>
          </SectionBlock>

          <SectionBlock title="Linked alerts">
            <div className="dim tiny">No active alerts for this device.</div>
          </SectionBlock>

          <SectionBlock title="Notes">
            {item.note ? <div className="sm" style={{ padding: 10, background:"var(--bg-2)", borderRadius: 4 }}>{item.note}</div> : <div className="dim tiny">No notes.</div>}
          </SectionBlock>
        </div>
        <div className="drawer-foot">
          <Btn variant="danger" icon="trash">Remove</Btn>
          <Btn variant="ghost">Cancel</Btn>
          <Btn variant="primary" icon="check">Save changes</Btn>
        </div>
      </div>
    </React.Fragment>
  );
};

const SectionBlock = ({ title, hint, children }) => (
  <div style={{ marginBottom: 18 }}>
    <div className="row" style={{ marginBottom: 8, gap: 8 }}>
      <span className="mono tiny" style={{ color: "var(--fg-2)", textTransform:"uppercase", letterSpacing: "0.08em" }}>{title}</span>
      {hint && <span className="dim tiny right">{hint}</span>}
    </div>
    {children}
  </div>
);

const MaintRow = ({ date, what }) => (
  <div className="row">
    <Icon name="wrench" size={12} className="ico"/>
    <span className="sm">{what}</span>
    <span className="dim tiny mono right">{date}</span>
  </div>
);

window.Equipment = Equipment;
