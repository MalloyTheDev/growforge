/* GrowForge — Environment monitoring screen */

const Environment = ({ room }) => {
  const { ROOMS, EQUIPMENT, SERIES } = window.GFData;
  const { Card, Badge, Btn, MetricCard, SectionHead } = window.GFC;
  const { LineChart, VpdChart, DayNightBars } = window.GFCharts;
  const roomObj = ROOMS.find(r => r.id === room) || ROOMS[0];
  const sensors = EQUIPMENT.filter(e => e.cat === "Sensors" && e.room === roomObj.id);
  const [range, setRange] = React.useState("24h");

  const tempSeries = range === "24h" ? SERIES.tempF : SERIES.tempF_7d;
  const rhSeries = range === "24h" ? SERIES.rh : SERIES.rh_7d;
  const vpdSeries = range === "24h" ? SERIES.vpd : SERIES.vpd_7d;
  const xLabels24 = ["09:00","12:00","15:00","18:00","21:00","00:00","03:00","06:00"];
  const xLabels7d = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  const xLabels = range === "24h" ? xLabels24 : xLabels7d;

  return (
    <div data-screen-label="02 Environment">
      <div className="page-head">
        <div>
          <h1 className="page-title">Environment</h1>
          <div className="page-sub">
            <span className="mono">{roomObj.name}</span> · sensor: Govee H5179 · last updated 32 sec ago
          </div>
        </div>
        <div className="row">
          <div className="chips">
            {["24h","7d","30d"].map(r => (
              <span key={r} className={"chip " + (range === r ? "active" : "")} onClick={() => setRange(r)}>{r}</span>
            ))}
          </div>
          <Btn icon="settings">Configure targets</Btn>
        </div>
      </div>

      {/* Current readings — large */}
      <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", marginBottom: 18 }}>
        <BigReading label="Temperature" value={roomObj.temp.toFixed(1)} unit="°F" target="75–82" status="ok" delta="↑ 1.2 in 1h"/>
        <BigReading label="Humidity" value={roomObj.rh} unit="% RH" target="50–60" status="ok" delta="↓ 0.8 in 1h"/>
        <BigReading label="VPD" value={roomObj.vpd.toFixed(2)} unit="kPa" target="1.2–1.5" status="ok" delta="ideal"/>
        <BigReading label="CO₂" value={roomObj.co2} unit="ppm" target="800–1200" status="ok" delta="ambient"/>
        <BigReading label="Dew Point" value="60.2" unit="°F" target="< 64" status="ok"/>
      </div>

      {/* Trends */}
      <div className="grid" style={{ gridTemplateColumns: "minmax(0, 1.5fr) minmax(0, 1fr)", gap: 18, marginBottom: 18 }}>
        <Card title={`Temperature · ${range}`} right={<span className="mono tiny dim">target 75–82°F</span>} pad={false}>
          <div style={{ padding: "10px 14px" }}>
            <LineChart data={tempSeries} w={760} h={220} color="var(--accent)" yMin={70} yMax={88} zone={[75, 82]} xLabels={xLabels}/>
          </div>
        </Card>
        <Card title="VPD zone chart" right={<span className="mono tiny dim">temp × RH</span>} pad={false}>
          <div style={{ padding: "10px 14px" }}>
            <VpdChart markerT={roomObj.temp} markerRh={roomObj.rh}/>
            <div className="row sm" style={{ marginTop: 8, justifyContent:"center", gap: 12 }}>
              <span className="badge ok"><span className="pip"/>Current</span>
              <span className="dim mono tiny">T {roomObj.temp.toFixed(1)}°F · RH {roomObj.rh}%</span>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)", gap: 18, marginBottom: 18 }}>
        <Card title={`Humidity · ${range}`} right={<span className="mono tiny dim">target 50–60%</span>} pad={false}>
          <div style={{ padding: "10px 14px" }}>
            <LineChart data={rhSeries} w={600} h={180} color="var(--sensor)" yMin={40} yMax={75} zone={[50, 60]} xLabels={xLabels}/>
          </div>
        </Card>
        <Card title={`VPD · ${range}`} right={<span className="mono tiny dim">target 1.2–1.5 kPa</span>} pad={false}>
          <div style={{ padding: "10px 14px" }}>
            <LineChart data={vpdSeries} w={600} h={180} color="var(--accent)" yMin={0.7} yMax={1.8} zone={[1.2, 1.5]} xLabels={xLabels}/>
          </div>
        </Card>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr)", gap: 18, marginBottom: 18 }}>
        <Card title="Day vs night · 7d" right={<span className="mono tiny dim">avg temperature</span>}>
          <DayNightBars dayVals={[78.1,78.6,78.2,77.9,78.5,78.0,78.4]} nightVals={[72.0,72.2,71.8,71.6,72.1,71.9,72.2]}/>
          <div className="row sm" style={{ marginTop: 4, justifyContent: "center", gap: 14 }}>
            <span className="row tiny"><span className="s-dot ok"/> Day avg <span className="mono">78.2°F</span></span>
            <span className="row tiny"><span className="s-dot off"/> Night avg <span className="mono">72.0°F</span></span>
          </div>
        </Card>

        <Card title="Target configuration">
          <div className="col" style={{ gap: 12 }}>
            <RangeRow label="Temperature" min={65} max={90} lo={75} hi={82} current={roomObj.temp} unit="°F"/>
            <RangeRow label="Humidity" min={20} max={90} lo={50} hi={60} current={roomObj.rh} unit="%"/>
            <RangeRow label="VPD" min={0.4} max={2} lo={1.2} hi={1.5} current={roomObj.vpd} unit="kPa"/>
            <RangeRow label="CO₂" min={400} max={1500} lo={800} hi={1200} current={roomObj.co2} unit="ppm"/>
          </div>
        </Card>

        <Card title="Sensor sources" right={<span className="mono tiny dim">{sensors.length} active</span>} pad={false}>
          <div className="col" style={{ gap: 0 }}>
            {sensors.map(s => (
              <div key={s.id} className="row" style={{ padding: "10px 14px", borderBottom: "1px solid var(--line-soft)" }}>
                <span className="s-dot ok" style={{ marginRight: 8 }}/>
                <div style={{ flex: 1 }}>
                  <div className="sm">{s.name}</div>
                  <div className="dim tiny mono">{s.mode}</div>
                </div>
                <div className="dim tiny mono">{s.lastSeen}</div>
              </div>
            ))}
            <div className="row" style={{ padding: "10px 14px" }}>
              <Btn icon="plus" variant="ghost">Pair new sensor</Btn>
              <span className="dim tiny mono right">BLE bridge: 1 active</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Warning states demo */}
      <Card title="Warning states" pad={false}>
        <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 0 }}>
          <WarnRow tone="ok" label="Temperature" msg="In target zone (78.4°F)" />
          <WarnRow tone="warn" label="Temperature high" msg="≥ 83°F · ramp inline fan" />
          <WarnRow tone="crit" label="Temperature critical" msg="≥ 87°F · pause CO₂, alert" />
          <WarnRow tone="ok" label="Humidity" msg="In target zone (54% RH)" />
          <WarnRow tone="warn" label="Humidity high" msg="≥ 65% RH in flower · risk: bud rot" />
          <WarnRow tone="crit" label="VPD critical low" msg="< 0.8 kPa · risk: transpiration stalled" />
        </div>
      </Card>
    </div>
  );
};

const BigReading = ({ label, value, unit, target, status, delta }) => (
  <div className="card">
    <div className="card-pad">
      <div className="row" style={{ marginBottom: 10 }}>
        <span className="mono tiny" style={{ color: "var(--fg-3)", textTransform:"uppercase", letterSpacing: "0.08em" }}>{label}</span>
        <span className="right"><span className={"s-dot " + status}/></span>
      </div>
      <div className="metric">
        <span className="val" style={{ fontSize: 36 }}>{value}</span>
        <span className="unit">{unit}</span>
      </div>
      <div className="row" style={{ marginTop: 6, gap: 10 }}>
        <span className="dim mono tiny">target {target}</span>
        {delta && <span className="mono tiny" style={{ color: "var(--accent)" }}>{delta}</span>}
      </div>
    </div>
  </div>
);

const RangeRow = ({ label, min, max, lo, hi, current, unit }) => {
  const span = max - min;
  const loPct = ((lo - min) / span) * 100;
  const hiPct = ((hi - min) / span) * 100;
  const cPct = ((current - min) / span) * 100;
  return (
    <div className="col">
      <div className="row">
        <span className="sm">{label}</span>
        <span className="right mono tiny dim">{lo}–{hi} {unit}</span>
      </div>
      <div className="range-track">
        <div className="zone" style={{ left: loPct + "%", width: (hiPct - loPct) + "%" }}/>
        <div className="marker" style={{ left: cPct + "%" }}/>
      </div>
      <div className="row">
        <span className="mono tiny dim">{min} {unit}</span>
        <span className="right mono tiny" style={{ color: "var(--fg-0)" }}>now {Number(current).toFixed(unit === "kPa" ? 2 : 1)} {unit}</span>
      </div>
    </div>
  );
};

const WarnRow = ({ tone, label, msg }) => (
  <div className="row" style={{ padding: "10px 14px", borderBottom: "1px solid var(--line-soft)", borderRight: "1px solid var(--line-soft)" }}>
    <span className={"s-dot " + tone} style={{ marginRight: 8 }}/>
    <div className="col" style={{ gap: 2 }}>
      <span className="sm">{label}</span>
      <span className="dim tiny mono">{msg}</span>
    </div>
  </div>
);

window.Environment = Environment;
