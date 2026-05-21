/* GrowForge — Rooms / Tents */

const Rooms = ({ go, setRoom }) => {
  const { ROOMS, PLANTS, EQUIPMENT, SERIES, ALERTS } = window.GFData;
  const { Card, Badge, Btn, StageBadge } = window.GFC;
  const { Sparkline } = window.GFCharts;

  return (
    <div data-screen-label="07 Rooms">
      <div className="page-head">
        <div>
          <h1 className="page-title">Rooms & Tents</h1>
          <div className="page-sub">{ROOMS.length} active spaces · {PLANTS.length} plants total · {EQUIPMENT.length} equipment items</div>
        </div>
        <div className="row">
          <Btn icon="export">Export layout</Btn>
          <Btn variant="primary" icon="plus">Add room</Btn>
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", marginBottom: 18 }}>
        {ROOMS.map(r => {
          const ps = PLANTS.filter(p => p.room === r.id);
          const eq = EQUIPMENT.filter(e => e.room === r.id);
          const al = ALERTS.filter(a => a.related === r.id && a.state !== "resolved");
          return (
            <div key={r.id} className="card" style={{ cursor:"pointer", transition: "border-color .12s" }}
                 onMouseEnter={e => e.currentTarget.style.borderColor = "var(--accent-line)"}
                 onMouseLeave={e => e.currentTarget.style.borderColor = "var(--line)"}
                 onClick={() => { setRoom(r.id); go("dashboard"); }}>
              <div className="card-pad">
                <div className="row" style={{ marginBottom: 12 }}>
                  <div className="col">
                    <span className="mono" style={{ fontSize: 14 }}>{r.name}</span>
                    <span className="dim tiny mono">{r.stage} · day {Math.max(...ps.map(p=>p.day), 0)} · light {r.light}</span>
                  </div>
                  <span className="right"><Badge tone={r.status === "ok" ? "ok" : "warn"} dot>{r.status === "ok" ? "stable" : "watch"}</Badge></span>
                </div>

                {/* room layout schematic */}
                <RoomDiagram room={r}/>

                <div className="grid" style={{ gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginTop: 12 }}>
                  <MiniMetric label="Temp" value={r.temp.toFixed(1)} unit="°F" series={SERIES.tempF.slice(0,12)} color="var(--accent)"/>
                  <MiniMetric label="RH" value={r.rh} unit="%" series={SERIES.rh.slice(0,12)} color="var(--sensor)"/>
                  <MiniMetric label="VPD" value={r.vpd.toFixed(2)} unit="kPa" series={SERIES.vpd.slice(0,12)} color="var(--accent)"/>
                </div>

                <div className="divider"/>

                <div className="row" style={{ gap: 12, flexWrap:"wrap" }}>
                  <span className="row tiny"><Icon name="plants" size={12}/> <span className="mono">{ps.length}</span> <span className="dim">plants</span></span>
                  <span className="row tiny"><Icon name="equip" size={12}/> <span className="mono">{eq.length}</span> <span className="dim">equipment</span></span>
                  <span className="row tiny"><Icon name="alerts" size={12}/> <span className="mono">{al.length}</span> <span className="dim">alerts</span></span>
                  <span className="right"><Btn variant="ghost">Open →</Btn></span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* equipment loadout per room */}
      <Card title="Equipment loadout · all rooms" pad={false}>
        <table className="tbl">
          <thead><tr><th>Room</th><th>Lights</th><th>Inline fan</th><th>Humidity</th><th>Sensors</th><th>Cameras</th><th className="num">Power</th></tr></thead>
          <tbody>
            {ROOMS.map(r => {
              const eq = EQUIPMENT.filter(e => e.room === r.id);
              const get = c => eq.filter(e => e.cat === c).map(e => e.name).join(", ") || "—";
              return (
                <tr key={r.id}>
                  <td><span className="mono">{r.short}</span></td>
                  <td className="dim">{get("Lights")}</td>
                  <td className="dim">{get("Inline Fan")}</td>
                  <td className="dim">{[get("Humidifier"), get("Dehumidifier")].filter(s => s !== "—").join(" + ") || "—"}</td>
                  <td className="dim">{get("Sensors")}</td>
                  <td className="dim">{get("Cameras")}</td>
                  <td className="num mono">{r.id === "tent-flower" ? "778 W" : r.id === "tent-veg" ? "227 W" : "0 W"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>
    </div>
  );
};

const MiniMetric = ({ label, value, unit, series, color }) => (
  <div className="col" style={{ gap: 2 }}>
    <span className="mono tiny dim" style={{ textTransform:"uppercase", letterSpacing: "0.06em" }}>{label}</span>
    <span className="mono" style={{ fontSize: 16 }}>{value}<span className="unit" style={{ fontSize: 11, marginLeft: 2 }}>{unit}</span></span>
    <window.GFCharts.Sparkline data={series} w={100} h={20} color={color}/>
  </div>
);

const RoomDiagram = ({ room }) => {
  const { PLANTS, EQUIPMENT } = window.GFData;
  const ps = PLANTS.filter(p => p.room === room.id);
  const isFlower = room.id === "tent-flower";
  const isVeg = room.id === "tent-veg";
  const isMom = room.id === "closet-mom";
  const w = 300, h = 130;
  return (
    <div style={{ position:"relative", border: "1px solid var(--line)", borderRadius: 6, padding: 10, background: "var(--bg-2)" }}>
      <svg viewBox={`0 0 ${w} ${h}`} width="100%" style={{ display:"block" }}>
        {/* tent outline */}
        <rect x={4} y={4} width={w-8} height={h-8} rx="3" fill="none" stroke="var(--line-strong)" strokeWidth="1.5"/>
        {/* light */}
        <rect x={20} y={10} width={w-40} height={10} fill="var(--bg-3)" stroke="var(--accent-line)"/>
        <text x={24} y={18} className="chart-y" style={{ fontSize: 8, fill:"var(--accent)" }}>LIGHT · {EQUIPMENT.find(e => e.room===room.id && e.cat==="Lights")?.name?.split(" ").slice(-1)[0] || "—"}</text>
        {/* fan + sensor */}
        <circle cx={w-18} cy={h/2} r="6" fill="var(--bg-3)" stroke="var(--sensor)" strokeWidth="1"/>
        <text x={w-30} y={h/2+12} className="chart-y" style={{ fontSize: 7 }}>FAN</text>
        <rect x={10} y={h-20} width={20} height={10} fill="var(--bg-3)" stroke="var(--accent-line)"/>
        <text x={10} y={h-22} className="chart-y" style={{ fontSize: 7 }}>SENSOR</text>
        {/* plants */}
        {ps.slice(0, 8).map((p, i) => {
          const cols = isFlower ? 3 : isVeg ? 3 : 4;
          const rows = Math.ceil(8 / cols);
          const col = i % cols, row = Math.floor(i / cols);
          const cx = 40 + col * ((w - 80) / Math.max(cols - 1, 1));
          const cy = 40 + row * 30;
          return (
            <g key={p.id}>
              <circle cx={cx} cy={cy} r="9" fill={p.health === "warn" ? "var(--warn-soft)" : "var(--accent-soft)"} stroke={p.health === "warn" ? "var(--warn)" : "var(--accent)"} strokeWidth="1"/>
              <text x={cx} y={cy + 3} textAnchor="middle" className="chart-y" style={{ fontSize: 7, fill: "var(--fg-0)" }}>{p.name}</text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

window.Rooms = Rooms;
