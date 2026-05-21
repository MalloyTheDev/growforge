/* GrowForge — Plants list & detail */

const Plants = ({ go, openModal, room }) => {
  const { PLANTS, ROOMS } = window.GFData;
  const { Card, Badge, Btn, StageBadge, PhotoSlot } = window.GFC;
  const [view, setView] = React.useState("grid");
  const [filter, setFilter] = React.useState("all");
  const [tag, setTag] = React.useState("all");

  const tagOptions = ["all", "veg", "flower", "mother", "clone", "seedling", "watch"];
  const stageFilter = ["all", "Seedling", "Vegetative", "Flowering", "Mother", "Rooting"];

  const list = PLANTS.filter(p => {
    if (filter !== "all" && p.stage !== filter) return false;
    if (tag !== "all" && !p.tags.includes(tag)) return false;
    return true;
  });

  return (
    <div data-screen-label="03 Plants">
      <div className="page-head">
        <div>
          <h1 className="page-title">Plants</h1>
          <div className="page-sub">{PLANTS.length} active · {PLANTS.filter(p => p.health === "warn").length} flagged · across {ROOMS.length} rooms</div>
        </div>
        <div className="row">
          <Btn icon="filter">Filter</Btn>
          <Btn icon="sort">Sort</Btn>
          <Btn variant="primary" icon="plus" onClick={() => openModal("plant")}>Add Plant</Btn>
        </div>
      </div>

      <div className="row" style={{ marginBottom: 14, flexWrap:"wrap", gap: 12 }}>
        <div className="chips">
          {stageFilter.map(s => <span key={s} className={"chip " + (filter === s ? "active" : "")} onClick={() => setFilter(s)}>{s}</span>)}
        </div>
        <div className="chips">
          {tagOptions.map(t => <span key={t} className={"chip " + (tag === t ? "active" : "")} onClick={() => setTag(t)}>#{t}</span>)}
        </div>
        <div className="row right" style={{ gap: 4 }}>
          <button className={"btn " + (view === "grid" ? "btn-primary" : "")} onClick={() => setView("grid")}><Icon name="dashboard" size={13}/>Grid</button>
          <button className={"btn " + (view === "list" ? "btn-primary" : "")} onClick={() => setView("list")}><Icon name="menu" size={13}/>List</button>
        </div>
      </div>

      {view === "grid" ? (
        <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))" }}>
          {list.map(p => <PlantCard key={p.id} plant={p} onClick={() => go("plant-detail", p.id)}/>)}
          {list.length === 0 && (
            <div className="empty card" style={{ gridColumn: "1/-1" }}>
              <Icon name="plants" size={36} className="ico"/>
              <div>No plants match the current filters.</div>
            </div>
          )}
        </div>
      ) : (
        <Card pad={false}>
          <table className="tbl">
            <thead><tr>
              <th>Plant</th><th>Strain</th><th>Stage</th><th className="num">Day</th><th>Room</th><th>Medium</th><th>Pot</th><th>Health</th><th>Last watered</th>
            </tr></thead>
            <tbody>
              {list.map(p => (
                <tr key={p.id} onClick={() => go("plant-detail", p.id)} style={{ cursor:"pointer" }}>
                  <td><span className="mono">{p.name}</span></td>
                  <td>{p.strain}</td>
                  <td><StageBadge stage={p.stage}/></td>
                  <td className="num">{p.day}</td>
                  <td className="dim">{ROOMS.find(r=>r.id===p.room)?.short}</td>
                  <td className="dim">{p.medium}</td>
                  <td className="dim mono">{p.pot}</td>
                  <td><span className={"s-dot " + (p.health === "ok" ? "ok" : "warn")}/></td>
                  <td className="dim">{p.lastWater}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
};

const PlantCard = ({ plant, onClick }) => {
  const { ROOMS } = window.GFData;
  const { StageBadge, Badge, PhotoSlot } = window.GFC;
  const r = ROOMS.find(x => x.id === plant.room);
  return (
    <div className="card" onClick={onClick} style={{ cursor: "pointer", transition: "border-color .12s" }}
         onMouseEnter={e => e.currentTarget.style.borderColor = "var(--accent-line)"}
         onMouseLeave={e => e.currentTarget.style.borderColor = "var(--line)"}>
      <PhotoSlot label={`${plant.name} · day ${plant.day}`} ratio="4 / 3" />
      <div className="card-pad" style={{ padding: 12 }}>
        <div className="row" style={{ marginBottom: 6 }}>
          <span className="mono" style={{ fontSize: 13 }}>{plant.name}</span>
          <span className="right">{plant.health === "warn" ? <Badge tone="warn" dot>watch</Badge> : <Badge tone="ok" dot>ok</Badge>}</span>
        </div>
        <div className="sm" style={{ marginBottom: 4 }}>{plant.strain}</div>
        <div className="row tiny dim mono" style={{ gap: 8 }}>
          <StageBadge stage={plant.stage}/>
          <span>day {plant.day}</span>
          <span className="right">{r?.short}</span>
        </div>
        <div className="divider"/>
        <div className="row tiny dim mono" style={{ gap: 10, flexWrap:"wrap" }}>
          <span>{plant.medium}</span>
          <span>·</span>
          <span>{plant.pot}</span>
        </div>
        <div className="row tiny mono" style={{ gap: 10, marginTop: 6 }}>
          <span><Icon name="drop" size={11}/> <span className="dim">{plant.lastWater}</span></span>
          <span className="right"><Icon name="leaf" size={11}/> <span className="dim">{plant.lastFeed}</span></span>
        </div>
      </div>
    </div>
  );
};

/* ────────────── Plant detail ─────────────────────────────────────────── */
const PlantDetail = ({ plantId, go }) => {
  const { PLANTS, LOG, ROOMS } = window.GFData;
  const { Card, Badge, Btn, StageBadge, PhotoSlot, SectionHead } = window.GFC;
  const { Sparkline, LineChart } = window.GFCharts;
  const p = PLANTS.find(x => x.id === plantId) || PLANTS[0];
  const r = ROOMS.find(x => x.id === p.room);
  const [tab, setTab] = React.useState("timeline");

  // Stage history (synthetic)
  const stageHistory = [
    { stage: "Germination", date: "Mar 02", days: 4 },
    { stage: "Seedling", date: "Mar 06", days: 10 },
    { stage: "Vegetative", date: "Mar 16", days: 28 },
    { stage: "Flowering", date: "Apr 13", days: 47, active: true },
  ];

  const plantLog = LOG.filter(l => l.plant.includes(p.name) || l.plant === "All flower plants" || l.plant === "All veg");

  return (
    <div data-screen-label="03 Plant detail">
      <div className="page-head">
        <div>
          <div className="row" style={{ gap: 6, marginBottom: 4, color:"var(--fg-2)", fontSize: 12 }}>
            <span style={{ cursor:"pointer" }} onClick={() => go("plants")}>Plants</span>
            <Icon name="chev" size={12}/>
            <span style={{ color: "var(--fg-0)" }} className="mono">{p.name}</span>
          </div>
          <h1 className="page-title">{p.strain} <span className="mono dim" style={{ fontSize: 14, fontWeight: 400, marginLeft: 8 }}>· {p.name}</span></h1>
          <div className="page-sub">
            <StageBadge stage={p.stage}/> <span className="mono">day {p.day}</span> · {r?.name} · {p.type} · {p.medium}, {p.pot}
          </div>
        </div>
        <div className="row">
          <Btn icon="plus">Add log</Btn>
          <Btn icon="edit">Edit</Btn>
          <Btn icon="more"/>
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr)", gap: 14, marginBottom: 18 }}>
        <PhotoSlot label={`${p.name} · latest`} ratio="1 / 1" />
        <PhotoSlot label="week 6" ratio="1 / 1" />
        <PhotoSlot label="week 5" ratio="1 / 1" />
      </div>

      <div className="grid" style={{ gridTemplateColumns: "minmax(0, 1.5fr) minmax(0, 1fr)", gap: 18 }}>
        <div className="col" style={{ gap: 18 }}>
          {/* Tabs */}
          <div className="tabs" style={{ marginBottom: 0 }}>
            {["timeline","events","training","measurements","tasks","notes"].map(t => (
              <span key={t} className={"tab " + (tab === t ? "active" : "")} onClick={() => setTab(t)}>{t}</span>
            ))}
          </div>

          {tab === "timeline" && (
            <Card title="Lifecycle timeline" pad={false}>
              <div style={{ padding: "16px 18px" }}>
                <div style={{ position:"relative" }}>
                  <div style={{ height: 2, background: "var(--line)", position:"absolute", left: 0, right: 0, top: 18 }}/>
                  <div className="row" style={{ justifyContent:"space-between", position:"relative" }}>
                    {stageHistory.map((s, i) => (
                      <div key={i} className="col" style={{ alignItems:"center", gap: 6, flex: 1, position:"relative" }}>
                        <div style={{ width: 12, height: 12, borderRadius:"50%", background: s.active ? "var(--accent)" : "var(--bg-3)", border: `2px solid ${s.active ? "var(--accent)" : "var(--line-strong)"}`, marginTop: 12, boxShadow: s.active ? "0 0 12px var(--accent)" : "none" }}/>
                        <span className="mono tiny" style={{ color: s.active ? "var(--fg-0)" : "var(--fg-2)" }}>{s.stage}</span>
                        <span className="mono tiny dim">{s.date}</span>
                        <span className="mono tiny dim">{s.days}d</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          )}

          {tab === "events" && (
            <Card title="Event history" pad={false}>
              <table className="tbl">
                <thead><tr><th>When</th><th>Type</th><th>Notes</th><th className="num">pH</th><th className="num">EC</th></tr></thead>
                <tbody>
                  {plantLog.slice(0, 10).map(l => (
                    <tr key={l.id}>
                      <td className="dim mono tiny">{l.t}</td>
                      <td><Badge tone={l.type === "Watering" || l.type === "Feeding" ? "cool" : l.type === "Pruning" || l.type === "Training" ? "ok" : "muted"}>{l.type}</Badge></td>
                      <td>{l.note}</td>
                      <td className="num mono dim">{l.ph || "—"}</td>
                      <td className="num mono dim">{l.ec || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          )}

          {tab === "training" && (
            <Card title="Training events" pad={false}>
              <div className="col" style={{ padding: 16, gap: 12 }}>
                <TrainingRow type="Topping" date="Mar 24" note="First top, removed apical meristem above 4th node."/>
                <TrainingRow type="LST" date="Apr 02" note="Pulled main branches outward, secured with soft ties."/>
                <TrainingRow type="Defoliation" date="Apr 18" note="Removed lower fan leaves under canopy."/>
                <TrainingRow type="Supercropping" date="Apr 25" note="Pinched 3 tallest colas to even canopy."/>
              </div>
            </Card>
          )}

          {tab === "measurements" && (
            <Card title="Measurements · 14d">
              <div className="row" style={{ gap: 18, flexWrap:"wrap" }}>
                <Measurement label="Height" value={p.height} delta="+8 cm / 7d"/>
                <Measurement label="Canopy width" value="62 cm" delta="+4 cm / 7d"/>
                <Measurement label="Node count" value="14"/>
                <Measurement label="Avg internode" value="4.2 cm"/>
              </div>
              <div className="divider"/>
              <SectionHead title="Height trend" sub="cm, last 14 days"/>
              <Sparkline data={[42,46,50,54,57,60,62,65,68,70,72,74,76,78]} w={600} h={80} color="var(--accent)" fill/>
            </Card>
          )}

          {tab === "tasks" && (
            <Card title="Tasks attached to this plant" pad={false}>
              <div className="col" style={{ gap: 0 }}>
                <TaskRow title="Water" due="Today · 18:00" priority="high"/>
                <TaskRow title="Top-dress with Gaia Green 4-4-4" due="Today · 19:00" priority="med"/>
                <TaskRow title="Defoliate lower canopy" due="Sat · 11:00" priority="med"/>
                <TaskRow title="Weekly photo" due="Tomorrow · 09:00" priority="low"/>
              </div>
            </Card>
          )}

          {tab === "notes" && (
            <Card title="Notes">
              <textarea defaultValue={p.note || "Healthy growth, on schedule. Watch for stretch in next 5 days."} style={{ width:"100%", minHeight: 120, background:"var(--bg-2)", border:"1px solid var(--line-strong)", borderRadius: 6, padding: 10, color:"var(--fg-0)" }}/>
            </Card>
          )}
        </div>

        <div className="col" style={{ gap: 18 }}>
          <Card title="Vitals">
            <div className="col" style={{ gap: 0 }}>
              <div className="kv"><span className="k">Strain</span><span className="v">{p.strain}</span></div>
              <div className="kv"><span className="k">Genetics</span><span className="v">{p.type}</span></div>
              <div className="kv"><span className="k">Stage</span><span className="v"><StageBadge stage={p.stage}/></span></div>
              <div className="kv"><span className="k">Age</span><span className="v">{p.day} days</span></div>
              <div className="kv"><span className="k">Medium</span><span className="v">{p.medium}</span></div>
              <div className="kv"><span className="k">Pot size</span><span className="v">{p.pot}</span></div>
              <div className="kv"><span className="k">Room</span><span className="v">{r?.short}</span></div>
              <div className="kv"><span className="k">Height</span><span className="v">{p.height}</span></div>
              <div className="kv"><span className="k">Last watered</span><span className="v">{p.lastWater}</span></div>
              <div className="kv"><span className="k">Last fed</span><span className="v">{p.lastFeed}</span></div>
            </div>
          </Card>

          <Card title="Health observations" right={<Badge tone={p.health === "ok" ? "ok" : "warn"}>{p.health === "ok" ? "healthy" : "watch"}</Badge>} pad={false}>
            <div className="col" style={{ gap: 0 }}>
              <HealthRow label="Leaves" status="ok" note="Vibrant green, no spotting."/>
              <HealthRow label="Stem" status="ok" note="Sturdy, no lean."/>
              <HealthRow label="Pests" status="ok" note="None observed in last 7d."/>
              <HealthRow label="Deficiencies" status={p.health === "warn" ? "warn" : "ok"} note={p.note || "None observed."}/>
            </div>
          </Card>

          <Card title="Tags">
            <div className="chips">
              {p.tags.map(t => <span key={t} className="chip active">#{t}</span>)}
              <span className="chip">+ add tag</span>
            </div>
          </Card>

          <Card title="Estimated harvest">
            <div className="metric">
              <span className="val" style={{ fontSize: 22 }}>~32d</span>
              <span className="unit">to harvest</span>
            </div>
            <div className="dim tiny mono" style={{ marginTop: 4 }}>Based on strain avg (9w flower) + current stage day {p.day - 47 < 0 ? p.day : p.day - 47}.</div>
          </Card>
        </div>
      </div>
    </div>
  );
};

const TrainingRow = ({ type, date, note }) => (
  <div className="row" style={{ gap: 12, alignItems:"flex-start" }}>
    <span className="badge ok"><span className="pip"/>{type}</span>
    <div style={{ flex: 1 }}>
      <div className="sm">{note}</div>
      <div className="dim tiny mono">{date}</div>
    </div>
  </div>
);

const Measurement = ({ label, value, delta }) => (
  <div className="col">
    <span className="dim mono tiny" style={{ textTransform:"uppercase", letterSpacing: "0.06em" }}>{label}</span>
    <span className="mono" style={{ fontSize: 18 }}>{value}</span>
    {delta && <span className="tiny" style={{ color: "var(--accent)" }}>{delta}</span>}
  </div>
);

const TaskRow = ({ title, due, priority }) => (
  <div className="row" style={{ padding: "10px 14px", borderBottom: "1px solid var(--line-soft)", gap: 10 }}>
    <input type="checkbox" style={{ accentColor: "var(--accent)" }}/>
    <div style={{ flex: 1 }}>
      <div className="sm">{title}</div>
      <div className="dim tiny mono">{due}</div>
    </div>
    <span className={"badge " + (priority === "high" ? "crit" : priority === "med" ? "warn" : "muted")}>{priority}</span>
  </div>
);

const HealthRow = ({ label, status, note }) => (
  <div className="row" style={{ padding: "10px 14px", borderBottom: "1px solid var(--line-soft)" }}>
    <span className={"s-dot " + status} style={{ marginRight: 8 }}/>
    <div className="col">
      <span className="sm">{label}</span>
      <span className="dim tiny">{note}</span>
    </div>
  </div>
);

window.Plants = Plants;
window.PlantDetail = PlantDetail;
