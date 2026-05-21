/* GrowForge — Alerts */

const Alerts = () => {
  const { ALERTS, ROOMS } = window.GFData;
  const { Card, Badge, Btn } = window.GFC;
  const [sev, setSev] = React.useState("all");
  const [state, setState] = React.useState("active");

  const list = ALERTS.filter(a => {
    if (sev !== "all" && a.sev !== sev) return false;
    if (state === "active" && a.state === "resolved") return false;
    if (state === "resolved" && a.state !== "resolved") return false;
    return true;
  });

  const counts = {
    crit: ALERTS.filter(a => a.sev === "crit" && a.state !== "resolved").length,
    warn: ALERTS.filter(a => a.sev === "warn" && a.state !== "resolved").length,
    info: ALERTS.filter(a => a.sev === "info" && a.state !== "resolved").length,
    ok: ALERTS.filter(a => a.state === "resolved").length,
  };

  return (
    <div data-screen-label="08 Alerts">
      <div className="page-head">
        <div>
          <h1 className="page-title">Alerts</h1>
          <div className="page-sub">{counts.crit} critical · {counts.warn} warnings · {counts.info} info · {counts.ok} resolved</div>
        </div>
        <div className="row">
          <Btn icon="check">Mark all read</Btn>
          <Btn icon="settings">Alert rules</Btn>
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", marginBottom: 18 }}>
        <SeverityCard label="Critical" value={counts.crit} tone="crit" />
        <SeverityCard label="Warning" value={counts.warn} tone="warn" />
        <SeverityCard label="Info" value={counts.info} tone="ok" />
        <SeverityCard label="Resolved (7d)" value={counts.ok} tone="muted" />
      </div>

      <div className="row" style={{ marginBottom: 14, gap: 8, flexWrap:"wrap" }}>
        <div className="chips">
          {["all","crit","warn","info","ok"].map(s => <span key={s} className={"chip " + (sev === s ? "active" : "")} onClick={() => setSev(s)}>{s}</span>)}
        </div>
        <div className="chips right">
          {["active","resolved","all"].map(s => <span key={s} className={"chip " + (state === s ? "active" : "")} onClick={() => setState(s)}>{s}</span>)}
        </div>
      </div>

      <Card pad={false}>
        <table className="tbl">
          <thead><tr><th>Severity</th><th>Alert</th><th>Source</th><th>Time</th><th>Suggested action</th><th>State</th></tr></thead>
          <tbody>
            {list.map(a => (
              <tr key={a.id}>
                <td>
                  <span className={"badge " + (a.sev === "crit" ? "crit" : a.sev === "warn" ? "warn" : a.sev === "info" ? "cool" : "ok")} dot>
                    <span className="pip"/>{a.sev}
                  </span>
                </td>
                <td><span className="sm">{a.title}</span></td>
                <td className="dim">{a.source}</td>
                <td className="dim mono tiny">{a.time}</td>
                <td className="sm" style={{ maxWidth: 320 }}>{a.suggest}</td>
                <td>{a.state === "open" ? <Badge tone="warn">open</Badge> : a.state === "ack" ? <Badge tone="muted">acknowledged</Badge> : <Badge tone="ok">resolved</Badge>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <Card title="Alert rules" right={<Btn icon="plus" variant="ghost">Add rule</Btn>} pad={false} style={{ marginTop: 18 }}>
        <table className="tbl">
          <thead><tr><th>Rule</th><th>Condition</th><th>Severity</th><th>Channel</th><th>State</th></tr></thead>
          <tbody>
            <tr><td>Temp high</td><td className="mono dim">temp ≥ 83°F · for 5 min</td><td><Badge tone="warn">warn</Badge></td><td className="dim">in-app</td><td><Badge tone="ok">active</Badge></td></tr>
            <tr><td>Temp critical</td><td className="mono dim">temp ≥ 87°F</td><td><Badge tone="crit">crit</Badge></td><td className="dim">in-app + push</td><td><Badge tone="ok">active</Badge></td></tr>
            <tr><td>RH high</td><td className="mono dim">RH ≥ 65% in flower</td><td><Badge tone="warn">warn</Badge></td><td className="dim">in-app</td><td><Badge tone="ok">active</Badge></td></tr>
            <tr><td>VPD out of range</td><td className="mono dim">VPD ∉ 1.0–1.6 · for 15 min</td><td><Badge tone="warn">warn</Badge></td><td className="dim">in-app</td><td><Badge tone="ok">active</Badge></td></tr>
            <tr><td>Sensor offline</td><td className="mono dim">no reading · 15 min</td><td><Badge tone="crit">crit</Badge></td><td className="dim">in-app + push</td><td><Badge tone="ok">active</Badge></td></tr>
            <tr><td>Missed watering</td><td className="mono dim">scheduled water overdue 4h</td><td><Badge tone="warn">warn</Badge></td><td className="dim">in-app</td><td><Badge tone="ok">active</Badge></td></tr>
            <tr><td>Maintenance due</td><td className="mono dim">since last clean ≥ 30d</td><td><Badge tone="cool">info</Badge></td><td className="dim">in-app</td><td><Badge tone="ok">active</Badge></td></tr>
          </tbody>
        </table>
      </Card>

      <div className="card" style={{ marginTop: 18, borderStyle: "dashed" }}>
        <div className="card-pad row" style={{ gap: 12 }}>
          <Icon name="info" size={14} className="ico"/>
          <div className="col">
            <span className="sm">Rule-based today · pattern recognition planned for v1.1</span>
            <span className="dim tiny mono">All suggestions above are deterministic rules. No automated diagnosis is generated yet — that's a future intelligence-layer feature.</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const SeverityCard = ({ label, value, tone }) => {
  const color = tone === "crit" ? "var(--crit)" : tone === "warn" ? "var(--warn)" : tone === "ok" ? "var(--accent)" : "var(--fg-1)";
  return (
    <div className="card">
      <div className="card-pad">
        <div className="row" style={{ marginBottom: 8 }}>
          <span className="mono tiny" style={{ color: "var(--fg-3)", textTransform:"uppercase", letterSpacing: "0.08em" }}>{label}</span>
          <span className={"s-dot " + (tone === "muted" ? "off" : tone)} style={{ marginLeft:"auto" }}/>
        </div>
        <span className="mono" style={{ fontSize: 32, color, fontWeight: 500 }}>{value}</span>
      </div>
    </div>
  );
};

window.Alerts = Alerts;
