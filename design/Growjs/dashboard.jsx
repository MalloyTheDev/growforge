/* GrowForge — Dashboard screen */

const Dashboard = ({ room, go, openModal }) => {
  const { ROOMS, PLANTS, EQUIPMENT, TASKS, ALERTS, LOG, SERIES } = window.GFData;
  const { Card, Badge, Btn, MetricCard, StageBadge, SectionHead, StatusRow } = window.GFC;
  const { LineChart, Sparkline } = window.GFCharts;

  const roomObj = ROOMS.find(r => r.id === room) || ROOMS[0];
  const roomPlants = PLANTS.filter(p => p.room === roomObj.id);
  const roomEq = EQUIPMENT.filter(e => e.room === roomObj.id);
  const roomTasks = TASKS.filter(t => t.room === roomObj.id && !t.done).slice(0, 4);
  const roomAlerts = ALERTS.filter(a => a.related === roomObj.id && a.state !== "resolved");
  const recentLogs = LOG.filter(l => l.room === roomObj.id || l.room === "—").slice(0, 4);

  // System health derived
  const eqOk = roomEq.filter(e => e.status === "ok").length;
  const eqWarn = roomEq.filter(e => e.status === "warn" || e.status === "crit").length;
  const taskOpen = TASKS.filter(t => !t.done).length;

  return (
    <div data-screen-label="01 Dashboard">
      {/* Page header */}
      <div className="page-head">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <div className="page-sub">
            <span className="mono">{roomObj.name}</span> · {roomObj.stage} · day {Math.max(...roomPlants.map(p => p.day))} ·
            <span style={{ marginLeft: 6 }} className="mono">{new Date().toLocaleDateString(undefined, { weekday:"short", month:"short", day:"numeric"})}</span>
          </div>
        </div>
        <div className="row">
          <Btn icon="plus" onClick={() => openModal("log")}>Add Log</Btn>
          <Btn icon="plus" onClick={() => openModal("task")}>Add Task</Btn>
          <Btn variant="primary" icon="leaf" onClick={() => openModal("plant")}>Add Plant</Btn>
        </div>
      </div>

      {/* System status strip */}
      <div className="card" style={{ marginBottom: 18 }}>
        <div className="card-pad" style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(160px, 1fr))", gap: 12, padding: "12px 16px" }}>
          <SysStat label="Operational" value={`${eqOk}/${roomEq.length}`} sub="devices online" tone="ok" />
          <SysStat label="Open alerts" value={roomAlerts.length} sub={roomAlerts.length ? "needs attention" : "all clear"} tone={roomAlerts.length ? "warn" : "ok"} />
          <SysStat label="Pending tasks" value={roomTasks.length} sub={`${taskOpen} total open`} tone={roomTasks.length > 3 ? "warn" : "ok"} />
          <SysStat label="Plants" value={roomPlants.length} sub={`${roomPlants.filter(p=>p.health==="warn").length} flagged`} tone="ok" />
          <SysStat label="Stage" value={roomObj.stage} sub={`${Math.max(...roomPlants.map(p => p.day))} days · ${roomObj.light}`} tone="cool" />
          <SysStat label="Harvest ETA" value="~32d" sub="Jun 22 (estimate)" tone="muted" />
        </div>
      </div>

      {/* Environment overview */}
      <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", marginBottom: 18 }}>
        <MetricCard icon="thermo" label="Temperature" value={roomObj.temp.toFixed(1)} unit="°F" status="ok" range="target 75–82" delta="↑ 1.2 from 1h ago" series={SERIES.tempF} />
        <MetricCard icon="drop" label="Humidity" value={roomObj.rh} unit="% RH" status="ok" range="target 45–60" delta="↓ 0.8 from 1h ago" series={SERIES.rh} color="var(--sensor)" />
        <MetricCard icon="trend" label="VPD" value={roomObj.vpd.toFixed(2)} unit="kPa" status="ok" range="ideal 1.2–1.5" delta="in zone" series={SERIES.vpd} />
        <MetricCard icon="bulb" label="Light cycle" value={roomObj.light} unit="hr" status="ok" range="day 14 of flower" delta="next off in 4h 12m" />
        <MetricCard icon="sensor" label="CO₂" value={roomObj.co2} unit="ppm" status="ok" range="target 800–1200" series={SERIES.co2} color="var(--violet)" />
      </div>

      {/* Two-column main */}
      <div className="grid" style={{ gridTemplateColumns: "minmax(0, 1.6fr) minmax(0, 1fr)", gap: 18 }}>
        <div className="col" style={{ gap: 18 }}>
          {/* Environment chart */}
          <Card title="Environmental trend · 24h" right={
            <div className="row" style={{ gap: 8 }}>
              <span className="badge ok"><span className="pip"/>Temperature</span>
              <span className="badge cool"><span className="pip"/>Humidity</span>
              <Btn variant="ghost" onClick={() => go("environment")}>Open monitor →</Btn>
            </div>
          } pad={false}>
            <div style={{ padding: "10px 14px 6px" }}>
              <LineChart data={SERIES.tempF} w={760} h={170} color="var(--accent)" yMin={70} yMax={88} zone={[75, 82]} xLabels={["09:00","12:00","15:00","18:00","21:00","00:00","03:00","06:00"]} />
              <div style={{ height: 1, background: "var(--line-soft)" }}/>
              <LineChart data={SERIES.rh} w={760} h={150} color="var(--sensor)" yMin={40} yMax={75} zone={[50, 60]} xLabels={["09:00","12:00","15:00","18:00","21:00","00:00","03:00","06:00"]} />
            </div>
          </Card>

          {/* Plants in this room */}
          <Card title={`Plants in ${roomObj.short} · ${roomPlants.length}`} right={<Btn variant="ghost" onClick={() => go("plants")}>All plants →</Btn>} pad={false}>
            <table className="tbl">
              <thead><tr>
                <th>Plant</th><th>Strain</th><th>Stage</th><th className="num">Day</th><th>Health</th><th>Last watered</th><th></th>
              </tr></thead>
              <tbody>
                {roomPlants.slice(0, 8).map(p => (
                  <tr key={p.id} onClick={() => go("plant-detail", p.id)} style={{ cursor:"pointer" }}>
                    <td><span className="mono">{p.name}</span></td>
                    <td>{p.strain}</td>
                    <td><StageBadge stage={p.stage}/></td>
                    <td className="num">{p.day}</td>
                    <td><span className={"s-dot " + (p.health === "ok" ? "ok" : "warn")}/></td>
                    <td className="dim">{p.lastWater}</td>
                    <td className="dim mono tiny">→</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>

        {/* Sidebar column */}
        <div className="col" style={{ gap: 18 }}>
          {/* Today's tasks */}
          <Card title={`Today · ${roomTasks.length} tasks`} right={<Btn variant="ghost" onClick={() => go("tasks")}>All →</Btn>} pad={false}>
            <div className="col" style={{ gap: 0 }}>
              {roomTasks.map(t => (
                <div key={t.id} className="row" style={{ padding: "10px 14px", borderBottom: "1px solid var(--line-soft)", gap: 10 }}>
                  <input type="checkbox" defaultChecked={t.done} style={{ accentColor: "var(--accent)" }}/>
                  <div style={{ flex: 1 }}>
                    <div className="sm">{t.title}</div>
                    <div className="dim tiny mono" style={{ marginTop: 2 }}>{t.due} · {t.related}</div>
                  </div>
                  <Badge tone={t.priority === "high" ? "crit" : t.priority === "med" ? "warn" : "muted"}>{t.priority}</Badge>
                </div>
              ))}
              {!roomTasks.length && <div className="empty">All clear for today.</div>}
            </div>
          </Card>

          {/* Alerts */}
          <Card title="Active alerts" right={<Btn variant="ghost" onClick={() => go("alerts")}>All →</Btn>} pad={false}>
            <div className="col" style={{ gap: 0 }}>
              {roomAlerts.length === 0 && <div className="empty"><Icon name="check" size={28} className="ico"/><div>No active alerts.</div></div>}
              {roomAlerts.map(a => (
                <div key={a.id} className="row" style={{ padding: "10px 14px", borderBottom: "1px solid var(--line-soft)", gap: 10, alignItems:"flex-start" }}>
                  <span className={"s-dot " + (a.sev === "crit" ? "crit" : a.sev === "warn" ? "warn" : "ok")} style={{ marginTop: 5 }}/>
                  <div style={{ flex: 1 }}>
                    <div className="sm">{a.title}</div>
                    <div className="dim tiny mono" style={{ marginTop: 2 }}>{a.source} · {a.time}</div>
                  </div>
                  <Badge tone={a.sev === "crit" ? "crit" : a.sev === "warn" ? "warn" : "ok"}>{a.sev}</Badge>
                </div>
              ))}
            </div>
          </Card>

          {/* Equipment status */}
          <Card title="Equipment in this room" right={<Btn variant="ghost" onClick={() => go("equipment")}>Manage →</Btn>} pad={false}>
            <div className="col" style={{ gap: 0 }}>
              {roomEq.slice(0, 6).map(e => (
                <div key={e.id} className="row" style={{ padding: "10px 14px", borderBottom: "1px solid var(--line-soft)", gap: 10 }}>
                  <span style={{ color: "var(--fg-3)" }}>
                    <Icon name={e.cat === "Lights" ? "bulb" : e.cat === "Inline Fan" || e.cat === "Clip Fans" ? "fan" : e.cat === "Humidifier" || e.cat === "Dehumidifier" ? "drop" : e.cat === "Sensors" ? "sensor" : e.cat === "Cameras" ? "cam" : "equip"} size={14}/>
                  </span>
                  <div style={{ flex: 1 }}>
                    <div className="sm">{e.name}</div>
                    <div className="dim tiny mono" style={{ marginTop: 2 }}>{e.cat} · {e.mode || "—"}</div>
                  </div>
                  <span className={"s-dot " + (e.status === "ok" ? "ok" : e.status === "warn" ? "warn" : e.status === "crit" ? "crit" : "off")}/>
                </div>
              ))}
            </div>
          </Card>

          {/* Recent grow log */}
          <Card title="Recent grow log" right={<Btn variant="ghost" onClick={() => go("growlog")}>Open log →</Btn>} pad={false}>
            <div className="col" style={{ gap: 0 }}>
              {recentLogs.map(l => (
                <div key={l.id} className="row" style={{ padding: "10px 14px", borderBottom: "1px solid var(--line-soft)", gap: 10, alignItems:"flex-start" }}>
                  <Badge tone={l.type === "Watering" || l.type === "Feeding" ? "cool" : l.type === "Training" || l.type === "Pruning" ? "ok" : l.type === "Issue Detected" ? "warn" : "muted"}>{l.type}</Badge>
                  <div style={{ flex: 1 }}>
                    <div className="sm">{l.note}</div>
                    <div className="dim tiny mono" style={{ marginTop: 2 }}>{l.t} · {l.plant}</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* Footer status bar */}
      <div className="card" style={{ marginTop: 18 }}>
        <div className="card-pad row" style={{ gap: 18, padding: "10px 16px", flexWrap:"wrap" }}>
          <span className="row sm"><span className="s-dot ok"/> <span className="mono tiny" style={{ color:"var(--fg-2)" }}>SYSTEM HEALTHY</span></span>
          <span className="dim tiny mono">Sensors: {EQUIPMENT.filter(e => e.cat === "Sensors").filter(e => e.status === "ok").length}/{EQUIPMENT.filter(e => e.cat === "Sensors").length}</span>
          <span className="dim tiny mono">Last sync: 32 sec ago</span>
          <span className="dim tiny mono">DB: 14 tables · 2.3 MB</span>
          <span className="dim tiny mono">Power: ~995 W</span>
          <span className="dim tiny mono right">v1.0.0 · production</span>
        </div>
      </div>
    </div>
  );
};

const SysStat = ({ label, value, sub, tone = "muted" }) => {
  const color = tone === "ok" ? "var(--accent)" : tone === "warn" ? "var(--warn)" : tone === "crit" ? "var(--crit)" : tone === "cool" ? "var(--sensor)" : "var(--fg-1)";
  return (
    <div className="col" style={{ gap: 4 }}>
      <span className="mono tiny" style={{ color: "var(--fg-3)", textTransform:"uppercase", letterSpacing: "0.08em" }}>{label}</span>
      <div className="row" style={{ gap: 8, alignItems:"baseline" }}>
        <span className="mono" style={{ fontSize: 22, color, fontWeight: 500 }}>{value}</span>
      </div>
      <span className="tiny dim">{sub}</span>
    </div>
  );
};

window.Dashboard = Dashboard;
