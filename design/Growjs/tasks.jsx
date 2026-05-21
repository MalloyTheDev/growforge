/* GrowForge — Tasks / Schedule */

const Tasks = ({ openModal }) => {
  const { TASKS, ROOMS } = window.GFData;
  const { Card, Badge, Btn } = window.GFC;
  const [view, setView] = React.useState("list");
  const [filter, setFilter] = React.useState("today");

  const open = TASKS.filter(t => !t.done);
  const today = open.filter(t => t.due.startsWith("Today"));
  const tomorrow = open.filter(t => t.due.startsWith("Tomorrow"));
  const later = open.filter(t => !t.due.startsWith("Today") && !t.due.startsWith("Tomorrow") && !t.due.startsWith("Yesterday"));
  const missed = TASKS.filter(t => !t.done && t.due.startsWith("Yesterday"));
  const completed = TASKS.filter(t => t.done);

  return (
    <div data-screen-label="06 Tasks">
      <div className="page-head">
        <div>
          <h1 className="page-title">Tasks</h1>
          <div className="page-sub">{open.length} open · {missed.length} missed · {completed.length} completed this week</div>
        </div>
        <div className="row">
          <div className="row" style={{ gap: 4 }}>
            <button className={"btn " + (view === "list" ? "btn-primary" : "")} onClick={() => setView("list")}><Icon name="menu" size={13}/>List</button>
            <button className={"btn " + (view === "cal" ? "btn-primary" : "")} onClick={() => setView("cal")}><Icon name="calendar" size={13}/>Calendar</button>
          </div>
          <Btn variant="primary" icon="plus" onClick={() => openModal("task")}>Add task</Btn>
        </div>
      </div>

      {view === "cal" ? <CalendarView/> : (
        <div className="grid" style={{ gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)", gap: 18 }}>
          <div className="col" style={{ gap: 18 }}>
            <TaskSection title="Today" items={today} highlight/>
            <TaskSection title="Tomorrow" items={tomorrow}/>
            <TaskSection title="Later this week" items={later}/>
          </div>
          <div className="col" style={{ gap: 18 }}>
            <TaskSection title="Missed" items={missed} tone="warn"/>
            <TaskSection title="Completed" items={completed} muted/>
            <Card title="Recurring tasks" pad={false}>
              <div className="col" style={{ gap: 0 }}>
                <RecurRow what="Water flower tent" cad="every 2 days"/>
                <RecurRow what="Top dress + microbes" cad="weekly · Sun 19:00"/>
                <RecurRow what="Weekly progress photos" cad="weekly · Fri 09:00"/>
                <RecurRow what="Inspect leaves for thrips" cad="weekly · Sun 10:00"/>
                <RecurRow what="Clean fan intake screens" cad="monthly"/>
                <RecurRow what="Calibrate pH/EC pen" cad="monthly"/>
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};

const TaskSection = ({ title, items, tone, highlight, muted }) => {
  const { Card, Badge } = window.GFC;
  return (
    <Card title={title} right={<span className="dim tiny mono">{items.length}</span>} pad={false}>
      <div className="col" style={{ gap: 0 }}>
        {items.length === 0 && <div className="empty" style={{ padding: "20px" }}><Icon name="check" size={28} className="ico"/><div>Nothing here.</div></div>}
        {items.map(t => (
          <div key={t.id} className="row" style={{ padding: "12px 14px", borderBottom: "1px solid var(--line-soft)", gap: 10, opacity: muted ? 0.6 : 1 }}>
            <input type="checkbox" defaultChecked={t.done} style={{ accentColor: "var(--accent)" }}/>
            <div style={{ flex: 1 }}>
              <div className="sm" style={{ textDecoration: t.done ? "line-through" : "none", color: t.done ? "var(--fg-2)" : "var(--fg-0)" }}>{t.title}</div>
              <div className="dim tiny mono" style={{ marginTop: 2 }}>
                {t.due} · {t.related} {t.recurring && <span style={{ color: "var(--sensor)" }}>· ↻ {t.recurring}</span>}
              </div>
            </div>
            <Badge tone={t.priority === "high" ? "crit" : t.priority === "med" ? "warn" : "muted"}>{t.priority}</Badge>
          </div>
        ))}
      </div>
    </Card>
  );
};

const RecurRow = ({ what, cad }) => (
  <div className="row" style={{ padding: "10px 14px", borderBottom: "1px solid var(--line-soft)" }}>
    <Icon name="history" size={13} className="ico"/>
    <div className="col" style={{ flex: 1 }}>
      <span className="sm">{what}</span>
      <span className="dim tiny mono">{cad}</span>
    </div>
    <Icon name="more" size={14} className="ico"/>
  </div>
);

const CalendarView = () => {
  const { TASKS } = window.GFData;
  const { Card, Badge } = window.GFC;
  // simple month grid
  const days = Array.from({ length: 35 }, (_, i) => i - 2); // offset
  const todayIdx = 12;
  const taskDays = { 9: 2, 10: 1, 12: 4, 13: 2, 14: 1, 15: 3, 17: 2, 19: 1, 21: 1 };
  return (
    <Card title="May 2026" right={<div className="row" style={{ gap: 6 }}><button className="btn btn-icon"><Icon name="chev" size={14} style={{ transform:"rotate(180deg)" }}/></button><button className="btn btn-icon"><Icon name="chev" size={14}/></button></div>} pad={false}>
      <div style={{ padding: 14 }}>
        <div className="row" style={{ gap: 0, borderBottom: "1px solid var(--line)" }}>
          {["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].map(d => (
            <div key={d} style={{ flex: 1, padding: 8, fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--fg-3)", textTransform: "uppercase", letterSpacing: "0.08em" }}>{d}</div>
          ))}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)" }}>
          {days.map((d, i) => (
            <div key={i} style={{ minHeight: 88, padding: 6, borderRight: "1px solid var(--line-soft)", borderBottom: "1px solid var(--line-soft)", background: i === todayIdx ? "var(--accent-soft)" : "transparent", position: "relative" }}>
              <div className="mono tiny" style={{ color: d < 1 ? "var(--fg-4)" : i === todayIdx ? "var(--accent)" : "var(--fg-2)" }}>{d < 1 ? 30 + d : d > 31 ? d - 31 : d}</div>
              {taskDays[d] && (
                <div className="col" style={{ gap: 3, marginTop: 6 }}>
                  {Array.from({ length: taskDays[d] }).map((_, k) => (
                    <div key={k} className="badge" style={{ fontSize: 9, padding: "1px 4px", justifyContent:"flex-start" }}>
                      <span className="pip" style={{ background: k === 0 ? "var(--warn)" : k === 1 ? "var(--accent)" : "var(--sensor)" }}/>
                      {k === 0 ? "water" : k === 1 ? "feed" : k === 2 ? "photo" : "inspect"}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};

window.Tasks = Tasks;
