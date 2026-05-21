/* GrowForge — Reports / Insights */

const Reports = () => {
  const { ROOMS, EQUIPMENT, TASKS, ALERTS, LOG, SERIES } = window.GFData;
  const { Card, Badge, Btn } = window.GFC;
  const { LineChart, Sparkline, Heatmap } = window.GFCharts;

  return (
    <div data-screen-label="09 Reports">
      <div className="page-head">
        <div>
          <h1 className="page-title">Reports</h1>
          <div className="page-sub">Operational summary · last 30 days</div>
        </div>
        <div className="row">
          <div className="chips">
            <span className="chip">7d</span>
            <span className="chip active">30d</span>
            <span className="chip">All grows</span>
          </div>
          <Btn icon="export">Export PDF</Btn>
          <Btn icon="export">Export CSV</Btn>
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", marginBottom: 18 }}>
        <KpiCard label="Environment stability" value="97.3" unit="%" sub="time in target zone" tone="ok"/>
        <KpiCard label="Task completion" value="91" unit="%" sub="42/46 completed on time" tone="ok"/>
        <KpiCard label="Watering frequency" value="11" unit="× / 30d" sub="avg 2.7 days between"/>
        <KpiCard label="Alert resolution" value="42" unit="min" sub="median time-to-ack" tone="ok"/>
        <KpiCard label="Equipment uptime" value="99.6" unit="%" sub="aggregate of 19 devices" tone="ok"/>
        <KpiCard label="Total power" value="298" unit="kWh" sub="~ $42.30 at $0.142/kWh"/>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "minmax(0, 1.4fr) minmax(0, 1fr)", gap: 18, marginBottom: 18 }}>
        <Card title="Environment in target zone · 30d" right={<span className="mono tiny dim">%/day</span>} pad={false}>
          <div style={{ padding: 14 }}>
            <Heatmap rows={3} cols={30} getVal={(r,c) => 0.4 + Math.sin(c/4+r) * 0.3 + Math.random() * 0.2}/>
            <div className="row" style={{ marginTop: 8, gap: 14 }}>
              <span className="row tiny"><span style={{ width:10, height:10, background:"oklch(0.5 0.08 145 / 0.15)" }}/> &lt; 80%</span>
              <span className="row tiny"><span style={{ width:10, height:10, background:"oklch(0.5 0.08 145 / 0.35)" }}/> 80–95%</span>
              <span className="row tiny"><span style={{ width:10, height:10, background:"oklch(0.5 0.08 145 / 0.55)" }}/> &gt; 95%</span>
              <span className="dim tiny mono right">Rows: temp / RH / VPD</span>
            </div>
          </div>
        </Card>

        <Card title="Growth stage timeline · current cycle" pad={false}>
          <div style={{ padding: 14 }}>
            <StageTimeline stages={[
              { stage: "Germination", days: 4, tone: "violet" },
              { stage: "Seedling", days: 10, tone: "ok" },
              { stage: "Vegetative", days: 28, tone: "cool" },
              { stage: "Flowering", days: 47, tone: "warn", active: true },
              { stage: "Flushing", days: 14, tone: "crit", projected: true },
              { stage: "Drying", days: 10, tone: "muted", projected: true },
              { stage: "Curing", days: 21, tone: "muted", projected: true },
            ]}/>
            <div className="row tiny dim mono" style={{ marginTop: 10, gap: 12 }}>
              <span><span className="s-dot ok"/> completed</span>
              <span><span className="s-dot warn"/> active</span>
              <span><span style={{ display:"inline-block", width:8, height:8, border:"1px dashed var(--fg-3)", borderRadius:"50%" }}/> projected</span>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)", gap: 18, marginBottom: 18 }}>
        <Card title="Temperature stability · 30d" right={<span className="badge ok"><span className="pip"/>96.4% in zone</span>} pad={false}>
          <div style={{ padding: 14 }}>
            <LineChart data={[...SERIES.tempF, ...SERIES.tempF.slice().reverse(), ...SERIES.tempF]} w={600} h={140} color="var(--accent)" yMin={70} yMax={88} zone={[75, 82]} xLabels={["Apr 21","Apr 28","May 5","May 12","May 19"]}/>
          </div>
        </Card>
        <Card title="Task completion rate · weekly" pad={false}>
          <div style={{ padding: 14 }}>
            <WeeklyBars vals={[88, 92, 95, 91, 89, 94, 91]}/>
          </div>
        </Card>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)", gap: 18, marginBottom: 18 }}>
        <Card title="Alert history · last 30d" pad={false}>
          <table className="tbl">
            <thead><tr><th>Date</th><th>Type</th><th>Sev</th><th>Resolved in</th></tr></thead>
            <tbody>
              <tr><td className="dim mono tiny">May 19</td><td>Sensor offline</td><td><Badge tone="crit">crit</Badge></td><td className="num mono">47m</td></tr>
              <tr><td className="dim mono tiny">May 19</td><td>Humidifier low</td><td><Badge tone="warn">warn</Badge></td><td className="num mono">12m</td></tr>
              <tr><td className="dim mono tiny">May 18</td><td>Temp spike</td><td><Badge tone="warn">warn</Badge></td><td className="num mono">18m</td></tr>
              <tr><td className="dim mono tiny">May 15</td><td>Missed watering</td><td><Badge tone="warn">warn</Badge></td><td className="num mono">4h</td></tr>
              <tr><td className="dim mono tiny">May 12</td><td>RH high</td><td><Badge tone="warn">warn</Badge></td><td className="num mono">22m</td></tr>
              <tr><td className="dim mono tiny">May 08</td><td>Calibration due</td><td><Badge tone="cool">info</Badge></td><td className="num mono">2d</td></tr>
            </tbody>
          </table>
        </Card>

        <Card title="Photo progress · WC-1 (flower)" pad={false}>
          <div style={{ padding: 14, display:"grid", gridTemplateColumns:"repeat(4, 1fr)", gap: 8 }}>
            {[1,2,3,4,5,6,7,8].map(w => (
              <div key={w} className="col" style={{ gap: 4 }}>
                <div className="photo" style={{ aspectRatio: "1 / 1", borderRadius: 4 }}><span>w{w}</span></div>
                <span className="dim tiny mono" style={{ textAlign:"center" }}>week {w}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card title="Equipment uptime · 30d" pad={false}>
        <table className="tbl">
          <thead><tr><th>Device</th><th>Category</th><th className="num">Uptime</th><th>Reliability</th></tr></thead>
          <tbody>
            <UptimeRow name="Spider Farmer SE7000" cat="Lights" pct={100}/>
            <UptimeRow name="Spider Farmer SE4500" cat="Lights" pct={100}/>
            <UptimeRow name="AC Infinity Cloudline T6" cat="Inline Fan" pct={99.8}/>
            <UptimeRow name="AC Infinity Cloudline T4" cat="Inline Fan" pct={99.9}/>
            <UptimeRow name="Levoit 300S" cat="Humidifier" pct={97.4}/>
            <UptimeRow name="Inkbird Dehumidifier" cat="Dehumidifier" pct={100}/>
            <UptimeRow name="Govee H5179 · Flower" cat="Sensor" pct={99.5}/>
            <UptimeRow name="Govee H5179 · Closet" cat="Sensor" pct={94.1}/>
            <UptimeRow name="Wyze Cam v3" cat="Camera" pct={99.0}/>
          </tbody>
        </table>
      </Card>
    </div>
  );
};

const KpiCard = ({ label, value, unit, sub, tone }) => {
  const color = tone === "ok" ? "var(--accent)" : tone === "warn" ? "var(--warn)" : "var(--fg-0)";
  return (
    <div className="card">
      <div className="card-pad">
        <span className="mono tiny" style={{ color: "var(--fg-3)", textTransform:"uppercase", letterSpacing: "0.08em" }}>{label}</span>
        <div className="metric" style={{ marginTop: 8 }}>
          <span className="val" style={{ fontSize: 24, color }}>{value}</span>
          <span className="unit">{unit}</span>
        </div>
        <span className="tiny dim" style={{ marginTop: 4, display:"block" }}>{sub}</span>
      </div>
    </div>
  );
};

const StageTimeline = ({ stages }) => {
  const total = stages.reduce((s, x) => s + x.days, 0);
  return (
    <div className="col" style={{ gap: 8 }}>
      <div className="row" style={{ height: 26, borderRadius: 4, overflow: "hidden", border: "1px solid var(--line)" }}>
        {stages.map((s, i) => (
          <div key={i} style={{
            flex: s.days,
            background: s.projected ? "transparent" : s.tone === "warn" ? "var(--warn-soft)" : s.tone === "cool" ? "var(--sensor-soft)" : s.tone === "violet" ? "var(--violet-soft)" : s.tone === "crit" ? "var(--crit-soft)" : "var(--accent-soft)",
            borderRight: i < stages.length - 1 ? "1px solid var(--line)" : "0",
            borderLeft: s.projected ? "1px dashed var(--fg-4)" : "0",
            display: "grid", placeItems: "center",
            color: s.projected ? "var(--fg-3)" : "var(--fg-1)",
            fontFamily: "var(--font-mono)", fontSize: 10,
            position: "relative",
          }}>
            {s.active && <span className="s-dot warn" style={{ position:"absolute", top: -4, right: 4 }}/>}
            {s.days}d
          </div>
        ))}
      </div>
      <div className="row" style={{ flexWrap:"wrap", gap: 6 }}>
        {stages.map((s, i) => (
          <span key={i} className="dim tiny mono" style={{ minWidth: 90 }}>{s.stage} · {s.days}d</span>
        ))}
      </div>
    </div>
  );
};

const WeeklyBars = ({ vals }) => {
  const w = 600, h = 140, padL = 30, padR = 6, padT = 14, padB = 22;
  const innerW = w - padL - padR, innerH = h - padT - padB;
  const barW = (innerW / vals.length) - 8;
  const max = 100;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" style={{ display:"block" }}>
      {[0, 50, 100].map(v => (
        <g key={v}>
          <line x1={padL} x2={w-padR} y1={padT + innerH - (v/max)*innerH} y2={padT + innerH - (v/max)*innerH} stroke="var(--line)" strokeDasharray="2 4"/>
          <text x={padL - 4} y={padT + innerH - (v/max)*innerH + 3} textAnchor="end" className="chart-y">{v}%</text>
        </g>
      ))}
      {vals.map((v, i) => {
        const x = padL + i * (innerW / vals.length) + 4;
        const barH = (v / max) * innerH;
        const y = padT + innerH - barH;
        return (
          <g key={i}>
            <rect x={x} y={y} width={barW} height={barH} fill="var(--accent)" opacity={0.6}/>
            <text x={x + barW/2} y={y - 4} textAnchor="middle" className="chart-y" style={{ fill: "var(--fg-0)" }}>{v}%</text>
            <text x={x + barW/2} y={h - 6} textAnchor="middle" className="chart-y">W{i+1}</text>
          </g>
        );
      })}
    </svg>
  );
};

const UptimeRow = ({ name, cat, pct }) => (
  <tr>
    <td className="sm">{name}</td>
    <td className="dim">{cat}</td>
    <td className="num mono">{pct.toFixed(1)}%</td>
    <td>
      <div className="row" style={{ gap: 8 }}>
        <div className="pbar" style={{ flex: 1 }}><i style={{ width: pct + "%", background: pct >= 99 ? "var(--accent)" : pct >= 95 ? "var(--warn)" : "var(--crit)" }}/></div>
      </div>
    </td>
  </tr>
);

window.Reports = Reports;
