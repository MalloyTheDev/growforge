/* GrowForge — Grow Log / journal */

const GrowLog = ({ openModal }) => {
  const { LOG, PLANTS, ROOMS } = window.GFData;
  const { Card, Badge, Btn } = window.GFC;
  const types = ["All","Watering","Feeding","Training","Pruning","Photo","Observation","Environment","Equipment","Stage Change","Pest Treatment","Clone Taken"];
  const [type, setType] = React.useState("All");
  const [q, setQ] = React.useState("");

  const list = LOG.filter(l => {
    if (type !== "All" && !l.type.toLowerCase().includes(type.toLowerCase())) return false;
    if (q && !l.note.toLowerCase().includes(q.toLowerCase()) && !l.plant.toLowerCase().includes(q.toLowerCase())) return false;
    return true;
  });

  // group by date label
  const grouped = list.reduce((acc, l) => {
    const day = l.t.split(" · ")[0];
    (acc[day] = acc[day] || []).push(l);
    return acc;
  }, {});

  return (
    <div data-screen-label="04 Grow Log">
      <div className="page-head">
        <div>
          <h1 className="page-title">Grow Log</h1>
          <div className="page-sub">Chronological audit trail · {LOG.length} entries</div>
        </div>
        <div className="row">
          <Btn icon="export">Export</Btn>
          <Btn variant="primary" icon="plus" onClick={() => openModal("log")}>Add log entry</Btn>
        </div>
      </div>

      <div className="row" style={{ marginBottom: 14, gap: 12, flexWrap:"wrap" }}>
        <div className="search" style={{ maxWidth: 340 }}>
          <Icon name="search" size={14}/>
          <input placeholder="Search log notes, plants, tags…" value={q} onChange={e => setQ(e.target.value)}/>
        </div>
        <div className="chips">
          {types.map(t => <span key={t} className={"chip " + (type === t ? "active" : "")} onClick={() => setType(t)}>{t}</span>)}
        </div>
      </div>

      <Card pad={false}>
        {Object.entries(grouped).map(([day, items]) => (
          <div key={day}>
            <div className="row" style={{ padding: "10px 16px", background: "var(--bg-2)", borderBottom: "1px solid var(--line)" }}>
              <span className="mono tiny" style={{ color: "var(--fg-2)", textTransform:"uppercase", letterSpacing: "0.08em" }}>{day}</span>
              <span className="dim tiny mono right">{items.length} entries</span>
            </div>
            {items.map(l => (
              <div key={l.id} className="row" style={{ padding: "12px 16px", borderBottom: "1px solid var(--line-soft)", gap: 14, alignItems:"flex-start" }}>
                <div className="col" style={{ width: 84, flex: "none" }}>
                  <span className="mono tiny dim">{l.t.split(" · ")[1]}</span>
                  <span className="dim tiny">{l.author === "system" ? "system" : "@you"}</span>
                </div>
                <div style={{ width: 4, alignSelf: "stretch", background: logTypeColor(l.type), borderRadius: 2 }}/>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="row" style={{ marginBottom: 4, gap: 8, flexWrap:"wrap" }}>
                    <Badge tone={logTypeTone(l.type)}>{l.type}</Badge>
                    <span className="dim tiny mono">{l.plant}</span>
                    {l.room && l.room !== "—" && <span className="dim tiny mono">· {ROOMS.find(r=>r.id===l.room)?.short || l.room}</span>}
                    {l.tags && l.tags.map(t => <span key={t} className="badge muted">#{t}</span>)}
                  </div>
                  <div className="sm">{l.note}</div>
                  <div className="row tiny dim mono" style={{ gap: 16, marginTop: 6 }}>
                    {l.ph != null && <span>pH <span style={{ color: "var(--fg-1)" }}>{l.ph}</span></span>}
                    {l.ec != null && <span>EC <span style={{ color: "var(--fg-1)" }}>{l.ec}</span></span>}
                    {l.ppm != null && <span>PPM <span style={{ color: "var(--fg-1)" }}>{l.ppm}</span></span>}
                    {l.water != null && <span>Water <span style={{ color: "var(--fg-1)" }}>{l.water} ml</span></span>}
                  </div>
                </div>
                {l.hasPhoto && <div style={{ width: 64, height: 64 }}><div className="photo" style={{ width: "100%", height: "100%", borderRadius: 4 }}><span>photo</span></div></div>}
              </div>
            ))}
          </div>
        ))}
      </Card>
    </div>
  );
};

function logTypeTone(t) {
  if (/water/i.test(t)) return "cool";
  if (/feed|train|prun/i.test(t)) return "ok";
  if (/photo/i.test(t)) return "violet";
  if (/issue|pest/i.test(t)) return "warn";
  if (/environ|equip/i.test(t)) return "muted";
  return "muted";
}
function logTypeColor(t) {
  if (/water/i.test(t)) return "var(--sensor)";
  if (/feed|train|prun/i.test(t)) return "var(--accent)";
  if (/photo/i.test(t)) return "var(--violet)";
  if (/issue|pest/i.test(t)) return "var(--warn)";
  return "var(--fg-4)";
}

window.GrowLog = GrowLog;
