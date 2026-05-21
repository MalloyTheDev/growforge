/* GrowForge — Shared components (Card, Badge, Button, etc) */

const Card = ({ title, right, children, pad = true, className = "" }) => (
  <div className={"card " + className}>
    {title && (
      <div className="card-head">
        <h3>{title}</h3>
        {right && <div className="right">{right}</div>}
      </div>
    )}
    <div className={pad ? "card-pad" : ""}>{children}</div>
  </div>
);

const Badge = ({ tone = "muted", children, dot = false }) => (
  <span className={"badge " + tone}>
    {dot && <span className="pip"/>}
    {children}
  </span>
);

const Btn = ({ variant = "", icon, children, onClick, title }) => {
  const cls = "btn " + (variant === "primary" ? "btn-primary" : variant === "ghost" ? "btn-ghost" : variant === "danger" ? "btn-danger" : "");
  return (
    <button className={cls} onClick={onClick} title={title}>
      {icon && <Icon name={icon} size={13}/>}
      {children}
    </button>
  );
};

const IconBtn = ({ icon, onClick, title, variant = "" }) => {
  const cls = "btn btn-icon " + (variant === "primary" ? "btn-primary" : variant === "ghost" ? "btn-ghost" : "");
  return (
    <button className={cls} onClick={onClick} title={title}>
      <Icon name={icon} size={14}/>
    </button>
  );
};

/* Metric card with sparkline */
const MetricCard = ({ label, value, unit, status = "ok", delta, series, range, color = "var(--accent)", icon }) => (
  <div className="card">
    <div className="card-pad">
      <div className="row" style={{ marginBottom: 8 }}>
        {icon && <span style={{ color: "var(--fg-2)" }}><Icon name={icon} size={14}/></span>}
        <span className="mono tiny" style={{ color: "var(--fg-2)", textTransform:"uppercase", letterSpacing:"0.08em" }}>{label}</span>
        <span className="right"><span className={"s-dot " + status}/></span>
      </div>
      <div className="metric">
        <span className="val">{value}</span>
        {unit && <span className="unit">{unit}</span>}
      </div>
      {(delta || range) && (
        <div className="row" style={{ marginTop: 6, gap: 10 }}>
          {delta && <span className="delta">{delta}</span>}
          {range && <span className="mono tiny dim">{range}</span>}
        </div>
      )}
      {series && (
        <div style={{ marginTop: 10 }}>
          <GFCharts.Sparkline data={series} w={260} h={28} color={color} fill />
        </div>
      )}
    </div>
  </div>
);

/* Stage badge */
const STAGE_COLORS = {
  "Germination": "violet",
  "Seedling": "ok",
  "Vegetative": "cool",
  "Flowering": "warn",
  "Flushing": "crit",
  "Drying": "muted",
  "Curing": "muted",
  "Harvested": "ok",
  "Mother": "ok",
  "Rooting": "violet",
  "Clone": "violet",
};
const StageBadge = ({ stage }) => (<Badge tone={STAGE_COLORS[stage] || "muted"} dot>{stage}</Badge>);

/* Photo placeholder with label */
const PhotoSlot = ({ label = "photo", ratio = "1 / 1", className = "" }) => (
  <div className={"photo " + className} style={{ aspectRatio: ratio, borderRadius: 6 }}>
    <span>{label}</span>
  </div>
);

/* Section header inside a page */
const SectionHead = ({ title, sub, right }) => (
  <div className="row" style={{ marginBottom: 12 }}>
    <div>
      <div style={{ fontSize: 13, fontWeight: 500 }}>{title}</div>
      {sub && <div className="dim tiny" style={{ marginTop: 2 }}>{sub}</div>}
    </div>
    {right && <div className="right">{right}</div>}
  </div>
);

/* Brand logo mark — hexagonal cell node */
const BrandMark = ({ size = 30 }) => (
  <svg viewBox="0 0 32 32" width={size} height={size}>
    <defs>
      <linearGradient id="bm-grad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stopColor="oklch(0.78 0.1 145)"/>
        <stop offset="100%" stopColor="oklch(0.5 0.08 145)"/>
      </linearGradient>
    </defs>
    {/* outer hex */}
    <path d="M16 2 L28 9 L28 23 L16 30 L4 23 L4 9 Z" fill="none" stroke="url(#bm-grad)" strokeWidth="1.5"/>
    {/* inner upward bar (forge mark) */}
    <path d="M11 22 L11 14 L16 10 L21 14 L21 22" fill="none" stroke="url(#bm-grad)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <circle cx="16" cy="16" r="1.6" fill="url(#bm-grad)"/>
  </svg>
);

/* Status pill row used in equipment cards */
const StatusRow = ({ status, mode }) => (
  <div className="row sm" style={{ gap: 8 }}>
    <span className={"s-dot " + (status === "ok" ? "ok" : status === "warn" ? "warn" : status === "crit" ? "crit" : "off")}/>
    <span className="muted mono tiny" style={{ textTransform:"uppercase", letterSpacing: "0.06em" }}>{status === "off" ? "Offline" : status === "ok" ? "Online" : status === "warn" ? "Attention" : "Critical"}</span>
    {mode && <span className="dim tiny right">{mode}</span>}
  </div>
);

window.GFC = { Card, Badge, Btn, IconBtn, MetricCard, StageBadge, PhotoSlot, SectionHead, BrandMark, StatusRow };
window.STAGE_COLORS = STAGE_COLORS;
