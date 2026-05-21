/* GrowForge — Icon set (custom, technical, line-only) */
const Icon = ({ name, size = 16, className = "ico", stroke = 1.6 }) => {
  const sp = { width: size, height: size, viewBox: "0 0 24 24", fill: "none",
    stroke: "currentColor", strokeWidth: stroke, strokeLinecap: "round", strokeLinejoin: "round",
    className };
  switch (name) {
    case "dashboard": return (<svg {...sp}><rect x="3" y="3" width="8" height="10" rx="1.2"/><rect x="3" y="15" width="8" height="6" rx="1.2"/><rect x="13" y="3" width="8" height="6" rx="1.2"/><rect x="13" y="11" width="8" height="10" rx="1.2"/></svg>);
    case "env": return (<svg {...sp}><path d="M12 3v3"/><path d="M3 21h18"/><path d="M5 21V11l7-5 7 5v10"/><path d="M9 21v-6h6v6"/></svg>);
    case "plants": return (<svg {...sp}><path d="M12 21V10"/><path d="M12 12c-3-1-5-4-5-7 3 0 6 2 5 7Z"/><path d="M12 14c3-1 5-4 5-7-3 0-6 2-5 7Z"/></svg>);
    case "log": return (<svg {...sp}><rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M8 8h8"/><path d="M8 12h8"/><path d="M8 16h5"/></svg>);
    case "equip": return (<svg {...sp}><circle cx="12" cy="12" r="3"/><path d="M12 2v3"/><path d="M12 19v3"/><path d="M2 12h3"/><path d="M19 12h3"/><path d="M5 5l2 2"/><path d="M17 17l2 2"/><path d="M19 5l-2 2"/><path d="M5 19l2-2"/></svg>);
    case "tasks": return (<svg {...sp}><rect x="3" y="4" width="18" height="17" rx="1.5"/><path d="M3 9h18"/><path d="M8 2v4"/><path d="M16 2v4"/><path d="M7.5 14l2 2 5-5"/></svg>);
    case "rooms": return (<svg {...sp}><rect x="3" y="6" width="18" height="14" rx="1"/><path d="M3 11h18"/><path d="M9 6v14"/><path d="M15 6v14"/><path d="M3 6l3-3h12l3 3"/></svg>);
    case "alerts": return (<svg {...sp}><path d="M12 3 2 20h20L12 3Z"/><path d="M12 10v5"/><circle cx="12" cy="17.5" r=".7" fill="currentColor"/></svg>);
    case "reports": return (<svg {...sp}><path d="M4 20V8"/><path d="M10 20V4"/><path d="M16 20v-9"/><path d="M22 20v-5"/><path d="M3 20h19"/></svg>);
    case "settings": return (<svg {...sp}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1.04 1.55V21a2 2 0 1 1-4 0v-.09A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.55-1.04H3a2 2 0 1 1 0-4h.09A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1.04-1.55V3a2 2 0 1 1 4 0v.09A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9c.05.42.27.8.62 1.07.27.21.62.34.97.37H21a2 2 0 1 1 0 4h-.09a1.7 1.7 0 0 0-1.51 1.04Z"/></svg>);
    case "search": return (<svg {...sp}><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>);
    case "bell": return (<svg {...sp}><path d="M6 8a6 6 0 1 1 12 0c0 7 3 8 3 8H3s3-1 3-8Z"/><path d="M10 21a2 2 0 0 0 4 0"/></svg>);
    case "plus": return (<svg {...sp}><path d="M12 5v14"/><path d="M5 12h14"/></svg>);
    case "x": return (<svg {...sp}><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>);
    case "menu": return (<svg {...sp}><path d="M3 6h18"/><path d="M3 12h18"/><path d="M3 18h18"/></svg>);
    case "chevdown": return (<svg {...sp}><path d="m6 9 6 6 6-6"/></svg>);
    case "chev": return (<svg {...sp}><path d="m9 6 6 6-6 6"/></svg>);
    case "filter": return (<svg {...sp}><path d="M3 5h18"/><path d="M6 12h12"/><path d="M10 19h4"/></svg>);
    case "sort": return (<svg {...sp}><path d="M7 4v16"/><path d="m3 8 4-4 4 4"/><path d="M17 20V4"/><path d="m21 16-4 4-4-4"/></svg>);
    case "more": return (<svg {...sp}><circle cx="5" cy="12" r="1.4" fill="currentColor"/><circle cx="12" cy="12" r="1.4" fill="currentColor"/><circle cx="19" cy="12" r="1.4" fill="currentColor"/></svg>);
    case "calendar": return (<svg {...sp}><rect x="3" y="4" width="18" height="17" rx="1.5"/><path d="M3 9h18"/><path d="M8 2v4"/><path d="M16 2v4"/></svg>);
    case "drop": return (<svg {...sp}><path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11Z"/></svg>);
    case "thermo": return (<svg {...sp}><path d="M14 14V5a2 2 0 0 0-4 0v9a4 4 0 1 0 4 0Z"/></svg>);
    case "fan": return (<svg {...sp}><circle cx="12" cy="12" r="2"/><path d="M12 10c-2-3-1-7 0-8 1 1 2 5 0 8Z"/><path d="M12 14c2 3 1 7 0 8-1-1-2-5 0-8Z"/><path d="M10 12c-3-2-7-1-8 0 1 1 5 2 8 0Z"/><path d="M14 12c3 2 7 1 8 0-1-1-5-2-8 0Z"/></svg>);
    case "bulb": return (<svg {...sp}><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12c1 1 2 2 2 4h4c0-2 1-3 2-4a7 7 0 0 0-4-12Z"/></svg>);
    case "cam": return (<svg {...sp}><rect x="2" y="6" width="14" height="12" rx="1.5"/><path d="m22 8-6 4 6 4Z"/></svg>);
    case "sensor": return (<svg {...sp}><circle cx="12" cy="12" r="2"/><path d="M8 8a6 6 0 0 0 0 8"/><path d="M16 8a6 6 0 0 1 0 8"/><path d="M5 5a10 10 0 0 0 0 14"/><path d="M19 5a10 10 0 0 1 0 14"/></svg>);
    case "leaf": return (<svg {...sp}><path d="M4 20s2-12 16-14c0 14-10 16-16 14Z"/><path d="M4 20l8-8"/></svg>);
    case "scissors": return (<svg {...sp}><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="m20 4-9.4 9.4"/><path d="m20 20-9.4-9.4"/></svg>);
    case "check": return (<svg {...sp}><path d="m5 12 5 5L20 7"/></svg>);
    case "export": return (<svg {...sp}><path d="M12 3v12"/><path d="m7 8 5-5 5 5"/><path d="M5 21h14"/></svg>);
    case "import": return (<svg {...sp}><path d="M12 21V9"/><path d="m7 16 5 5 5-5"/><path d="M5 3h14"/></svg>);
    case "tag": return (<svg {...sp}><path d="M3 12V4h8l10 10-8 8L3 12Z"/><circle cx="7.5" cy="7.5" r="1.2" fill="currentColor"/></svg>);
    case "user": return (<svg {...sp}><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>);
    case "play": return (<svg {...sp}><path d="m6 4 14 8L6 20Z"/></svg>);
    case "pause": return (<svg {...sp}><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>);
    case "wrench": return (<svg {...sp}><path d="M15 4a4 4 0 0 1 4 5l-9 9a3 3 0 1 1-4-4l9-9a4 4 0 0 1 0 0Z"/></svg>);
    case "warning": return (<svg {...sp}><path d="M12 3 2 20h20L12 3Z"/><path d="M12 10v5"/><circle cx="12" cy="17.5" r=".7" fill="currentColor"/></svg>);
    case "moon": return (<svg {...sp}><path d="M21 13A9 9 0 1 1 11 3a7 7 0 0 0 10 10Z"/></svg>);
    case "sun": return (<svg {...sp}><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="M4 12H2"/><path d="M22 12h-2"/><path d="m5 5 1.4 1.4"/><path d="m17.6 17.6 1.4 1.4"/><path d="m5 19 1.4-1.4"/><path d="m17.6 6.4 1.4-1.4"/></svg>);
    case "trend": return (<svg {...sp}><path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/></svg>);
    case "history": return (<svg {...sp}><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/><path d="M12 8v5l3 2"/></svg>);
    case "info": return (<svg {...sp}><circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><circle cx="12" cy="8" r=".8" fill="currentColor"/></svg>);
    case "edit": return (<svg {...sp}><path d="M4 20h4l11-11-4-4L4 16Z"/><path d="m14 5 4 4"/></svg>);
    case "trash": return (<svg {...sp}><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M6 6v14a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>);
    case "circle": return (<svg {...sp}><circle cx="12" cy="12" r="9"/></svg>);
    default: return (<svg {...sp}><rect x="3" y="3" width="18" height="18" rx="2"/></svg>);
  }
};

window.Icon = Icon;
