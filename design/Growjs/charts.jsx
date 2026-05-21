/* GrowForge — Shared chart components (inline SVG) */

const Sparkline = ({ data, w = 120, h = 36, color = "var(--accent)", fill = false, yMin, yMax }) => {
  if (!data || !data.length) return null;
  const min = yMin != null ? yMin : Math.min(...data);
  const max = yMax != null ? yMax : Math.max(...data);
  const range = max - min || 1;
  const stepX = w / (data.length - 1);
  const pts = data.map((v, i) => [i * stepX, h - ((v - min) / range) * (h - 4) - 2]);
  const d = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ");
  const area = `${d} L ${w} ${h} L 0 ${h} Z`;
  const gid = "sg-" + Math.random().toString(36).slice(2,8);
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      {fill && (
        <defs>
          <linearGradient id={gid} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
      )}
      {fill && <path d={area} fill={`url(#${gid})`} />}
      <path d={d} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round"/>
    </svg>
  );
};

const LineChart = ({ data, w = 600, h = 200, color = "var(--accent)", yMin, yMax, yLabel = "", zone, xLabels }) => {
  if (!data || !data.length) return null;
  const padL = 40, padR = 14, padT = 14, padB = 24;
  const min = yMin != null ? yMin : Math.min(...data) - 1;
  const max = yMax != null ? yMax : Math.max(...data) + 1;
  const range = max - min || 1;
  const innerW = w - padL - padR;
  const innerH = h - padT - padB;
  const stepX = innerW / (data.length - 1);
  const pts = data.map((v, i) => [padL + i * stepX, padT + innerH - ((v - min) / range) * innerH]);
  const d = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ");
  const area = `${d} L ${padL + innerW} ${padT + innerH} L ${padL} ${padT + innerH} Z`;
  const yTicks = 4;
  const ticks = Array.from({ length: yTicks + 1 }, (_, i) => min + (range * i) / yTicks);
  const gid = "ag-" + Math.random().toString(36).slice(2,8);
  // zone rect
  let zoneRect = null;
  if (zone) {
    const y1 = padT + innerH - ((zone[1] - min) / range) * innerH;
    const y2 = padT + innerH - ((zone[0] - min) / range) * innerH;
    zoneRect = <rect x={padL} y={y1} width={innerW} height={Math.max(0, y2 - y1)} className="chart-zone" />;
  }
  return (
    <svg width="100%" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" style={{ display:"block" }}>
      <defs>
        <linearGradient id={gid} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      {zoneRect}
      {ticks.map((t, i) => {
        const y = padT + innerH - ((t - min) / range) * innerH;
        return (
          <g key={i}>
            <line x1={padL} x2={w - padR} y1={y} y2={y} className="chart-grid" strokeDasharray={i === 0 || i === yTicks ? "" : "2 4"} />
            <text x={padL - 6} y={y + 3} textAnchor="end" className="chart-y">{(+t.toFixed(t > 100 ? 0 : 1))}</text>
          </g>
        );
      })}
      <path d={area} fill={`url(#${gid})`} />
      <path d={d} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round"/>
      {xLabels && xLabels.map((lbl, i) => {
        const idx = Math.round((i / (xLabels.length - 1)) * (data.length - 1));
        const x = padL + idx * stepX;
        return <text key={i} x={x} y={h - 6} textAnchor={i === 0 ? "start" : i === xLabels.length - 1 ? "end" : "middle"} className="chart-y">{lbl}</text>;
      })}
      {yLabel && <text x={padL - 28} y={padT + 4} className="chart-y" transform={`rotate(-90 ${padL - 28} ${padT + 4})`}>{yLabel}</text>}
    </svg>
  );
};

/* VPD chart — temperature vs RH grid showing zones */
const VpdChart = ({ markerT = 78.4, markerRh = 54 }) => {
  // X = temp 65-85F, Y = RH 30-80
  const w = 360, h = 220, padL = 32, padR = 8, padT = 12, padB = 22;
  const tMin = 65, tMax = 85, rMin = 30, rMax = 80;
  const innerW = w - padL - padR, innerH = h - padT - padB;
  const tx = t => padL + ((t - tMin) / (tMax - tMin)) * innerW;
  const ry = r => padT + innerH - ((r - rMin) / (rMax - rMin)) * innerH;
  // Simplified VPD zones (idealized)
  // dryer zone: low RH at low T (transpiration stress, propagation)
  // ideal flower: ~75-82F at ~50-55% RH
  // danger: high RH at high T
  const zones = [
    { name: "propagation", color: "oklch(0.5 0.08 230 / 0.18)", x: tx(65), y: ry(80), w: tx(74) - tx(65), h: ry(60) - ry(80) },
    { name: "veg", color: "oklch(0.5 0.08 145 / 0.16)", x: tx(72), y: ry(70), w: tx(80) - tx(72), h: ry(55) - ry(70) },
    { name: "flower", color: "oklch(0.55 0.08 145 / 0.28)", x: tx(75), y: ry(60), w: tx(82) - tx(75), h: ry(40) - ry(60) },
    { name: "danger", color: "oklch(0.5 0.13 25 / 0.18)", x: tx(78), y: ry(80), w: tx(85) - tx(78), h: ry(65) - ry(80) },
  ];
  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" style={{ display:"block" }}>
      <rect x={padL} y={padT} width={innerW} height={innerH} fill="var(--bg-2)" />
      {zones.map((z, i) => (<rect key={i} x={z.x} y={z.y} width={z.w} height={z.h} fill={z.color} />))}
      {/* grid */}
      {[30,40,50,60,70,80].map(r => (
        <g key={r}>
          <line x1={padL} x2={w-padR} y1={ry(r)} y2={ry(r)} stroke="var(--line)" strokeDasharray="2 4" />
          <text x={padL - 4} y={ry(r) + 3} textAnchor="end" className="chart-y">{r}</text>
        </g>
      ))}
      {[65,70,75,80,85].map(t => (
        <g key={t}>
          <line x1={tx(t)} x2={tx(t)} y1={padT} y2={padT+innerH} stroke="var(--line)" strokeDasharray="2 4" />
          <text x={tx(t)} y={h - 6} textAnchor="middle" className="chart-y">{t}°</text>
        </g>
      ))}
      {/* labels */}
      <text x={tx(70)} y={ry(74)} className="chart-y" style={{fontSize:9}}>PROPAGATION</text>
      <text x={tx(75)} y={ry(64)} className="chart-y" style={{fontSize:9}}>VEG</text>
      <text x={tx(78)} y={ry(52)} className="chart-y" style={{fontSize:9, fill:"var(--accent)"}}>IDEAL FLOWER</text>
      <text x={tx(81)} y={ry(72)} className="chart-y" style={{fontSize:9, fill:"var(--crit)"}}>DANGER</text>
      {/* current marker */}
      <line x1={tx(markerT)} x2={tx(markerT)} y1={padT} y2={padT+innerH} stroke="var(--fg-0)" strokeOpacity="0.4" strokeDasharray="3 3"/>
      <line x1={padL} x2={w-padR} y1={ry(markerRh)} y2={ry(markerRh)} stroke="var(--fg-0)" strokeOpacity="0.4" strokeDasharray="3 3"/>
      <circle cx={tx(markerT)} cy={ry(markerRh)} r="5" fill="var(--fg-0)" stroke="var(--bg-0)" strokeWidth="2"/>
    </svg>
  );
};

/* Day/Night bar chart */
const DayNightBars = ({ dayVals, nightVals, color = "var(--accent)" }) => {
  const w = 300, h = 90, padL = 30, padR = 6, padT = 8, padB = 18;
  const innerW = w - padL - padR, innerH = h - padT - padB;
  const allVals = [...dayVals, ...nightVals];
  const max = Math.max(...allVals) * 1.1;
  const min = Math.min(...allVals) * 0.9;
  const range = max - min;
  const N = dayVals.length;
  const groupW = innerW / N;
  const barW = (groupW - 4) / 2;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" style={{ display:"block" }}>
      {[0, 1].map(i => {
        const v = min + (range * i);
        const y = padT + innerH - ((v - min) / range) * innerH;
        return <line key={i} x1={padL} x2={w-padR} y1={y} y2={y} stroke="var(--line)" strokeDasharray="2 4"/>;
      })}
      {dayVals.map((d, i) => {
        const n = nightVals[i];
        const xBase = padL + i * groupW + 2;
        const dh = ((d - min) / range) * innerH;
        const nh = ((n - min) / range) * innerH;
        const dy = padT + innerH - dh;
        const ny = padT + innerH - nh;
        return (
          <g key={i}>
            <rect x={xBase} y={dy} width={barW} height={dh} fill={color} />
            <rect x={xBase + barW + 2} y={ny} width={barW} height={nh} fill="var(--fg-3)" opacity="0.5" />
          </g>
        );
      })}
      {["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].map((lbl, i) => (
        <text key={i} x={padL + i * groupW + groupW / 2} y={h - 5} textAnchor="middle" className="chart-y">{lbl}</text>
      ))}
    </svg>
  );
};

/* Heatmap calendar (24 cols × N rows) */
const Heatmap = ({ rows = 7, cols = 24, getVal, label = "" }) => {
  const cellW = 16, cellH = 14, gap = 2;
  const w = cols * (cellW + gap), h = rows * (cellH + gap);
  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" style={{ display:"block" }}>
      {Array.from({ length: rows }).map((_, r) =>
        Array.from({ length: cols }).map((_, c) => {
          const v = getVal ? getVal(r, c) : Math.random();
          return <rect key={`${r}-${c}`} x={c * (cellW + gap)} y={r * (cellH + gap)} width={cellW} height={cellH} rx="1.5" fill={`oklch(0.5 0.08 145 / ${0.08 + v * 0.5})`} />;
        })
      )}
    </svg>
  );
};

window.GFCharts = { Sparkline, LineChart, VpdChart, DayNightBars, Heatmap };
