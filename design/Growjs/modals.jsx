/* GrowForge — Add modals (Log, Plant, Task, Equipment) */

const Modal = ({ kind, onClose }) => {
  const { Btn } = window.GFC;
  const title = kind === "log" ? "Add log entry" : kind === "plant" ? "Add plant" : kind === "task" ? "Add task" : "Add equipment";
  return (
    <React.Fragment>
      <div className="scrim" onClick={onClose}/>
      <div className="drawer">
        <div className="drawer-head">
          <Icon name={kind === "log" ? "log" : kind === "plant" ? "leaf" : kind === "task" ? "tasks" : "equip"} size={18}/>
          <h2>{title}</h2>
          <span className="right"><Btn icon="x" variant="ghost" onClick={onClose}/></span>
        </div>
        <div className="drawer-body">
          {kind === "log" && <LogForm/>}
          {kind === "plant" && <PlantForm/>}
          {kind === "task" && <TaskForm/>}
          {kind === "equipment" && <EquipForm/>}
        </div>
        <div className="drawer-foot">
          <Btn variant="ghost" onClick={onClose}>Cancel</Btn>
          <Btn variant="primary" icon="check" onClick={onClose}>Save</Btn>
        </div>
      </div>
    </React.Fragment>
  );
};

const LogForm = () => {
  const { PLANTS, ROOMS } = window.GFData;
  const types = ["Watering","Feeding","Training","Pruning","Photo","Observation","Environment","Equipment","Stage Change","Pest Treatment","Other"];
  const [type, setType] = React.useState("Watering");
  const [related, setRelated] = React.useState([]);
  return (
    <div>
      <div className="field">
        <label>Type</label>
        <div className="chips">{types.map(t => <span key={t} className={"chip " + (type === t ? "active" : "")} onClick={() => setType(t)}>{t}</span>)}</div>
      </div>
      <div className="field-row">
        <div className="field">
          <label>Date</label>
          <input type="text" defaultValue="2026-05-21"/>
        </div>
        <div className="field">
          <label>Time</label>
          <input type="text" defaultValue="18:00"/>
        </div>
      </div>
      <div className="field">
        <label>Related plants</label>
        <div className="chips" style={{ maxHeight: 100, overflow: "auto" }}>
          {PLANTS.map(p => {
            const on = related.includes(p.id);
            return <span key={p.id} className={"chip " + (on ? "active" : "")} onClick={() => setRelated(on ? related.filter(x => x !== p.id) : [...related, p.id])}>{p.name} <span className="dim">· {p.strain}</span></span>;
          })}
        </div>
      </div>
      <div className="field">
        <label>Room</label>
        <select>{ROOMS.map(r => <option key={r.id}>{r.name}</option>)}</select>
      </div>
      {(type === "Watering" || type === "Feeding") && (
        <div className="field-row">
          <div className="field"><label>pH</label><input defaultValue="6.4"/></div>
          <div className="field"><label>EC (mS/cm)</label><input defaultValue="1.1"/></div>
        </div>
      )}
      {(type === "Watering" || type === "Feeding") && (
        <div className="field-row">
          <div className="field"><label>Volume (ml)</label><input defaultValue="3785"/></div>
          <div className="field"><label>Mix / amendment</label><input placeholder="e.g. Gaia Green 4-4-4, 2 tbsp/gal"/></div>
        </div>
      )}
      <div className="field">
        <label>Notes</label>
        <textarea placeholder="What did you observe / what did you do? Be specific — this becomes the audit trail."/>
      </div>
      <div className="field">
        <label>Photo</label>
        <div className="photo" style={{ aspectRatio: "16 / 6", borderRadius: 6, borderStyle: "dashed", borderColor:"var(--line-strong)" }}><span>drop photo · or click</span></div>
      </div>
      <div className="field">
        <label>Tags</label>
        <div className="chips">
          {["watch","fix-soon","milestone","photo","week-7"].map(t => <span key={t} className="chip">#{t}</span>)}
        </div>
      </div>
    </div>
  );
};

const PlantForm = () => {
  const { ROOMS } = window.GFData;
  return (
    <div>
      <div className="field-row">
        <div className="field"><label>Plant name / tag</label><input placeholder="e.g. WC-3"/></div>
        <div className="field"><label>Strain</label><input placeholder="Wedding Cake"/></div>
      </div>
      <div className="field-row">
        <div className="field">
          <label>Genetics</label>
          <select><option>Photoperiod · Feminized</option><option>Photoperiod · Regular</option><option>Autoflower</option><option>Clone</option></select>
        </div>
        <div className="field">
          <label>Initial stage</label>
          <select><option>Germination</option><option>Seedling</option><option>Vegetative</option><option>Mother</option></select>
        </div>
      </div>
      <div className="field-row">
        <div className="field"><label>Start date</label><input defaultValue="2026-05-21"/></div>
        <div className="field"><label>Room / tent</label><select>{ROOMS.map(r => <option key={r.id}>{r.name}</option>)}</select></div>
      </div>
      <div className="field-row">
        <div className="field">
          <label>Medium</label>
          <select><option>Living Soil</option><option>Coco/Perlite</option><option>Soil (Organic)</option><option>Rockwool</option><option>DWC</option></select>
        </div>
        <div className="field">
          <label>Pot size</label>
          <select><option>1 gal</option><option>3 gal fabric</option><option>5 gal fabric</option><option>7 gal fabric</option></select>
        </div>
      </div>
      <div className="field"><label>Notes</label><textarea placeholder="Lineage, origin, breeder, observations…"/></div>
      <div className="field">
        <label>Tags</label>
        <div className="chips">
          {["seedling","veg","flower","mother","clone","auto","feminized","keeper"].map(t => <span key={t} className="chip">#{t}</span>)}
        </div>
      </div>
    </div>
  );
};

const TaskForm = () => {
  const { ROOMS, PLANTS } = window.GFData;
  return (
    <div>
      <div className="field"><label>Title</label><input placeholder="e.g. Water flower tent (round 1)"/></div>
      <div className="field-row">
        <div className="field"><label>Due date</label><input defaultValue="2026-05-21"/></div>
        <div className="field"><label>Due time</label><input defaultValue="18:00"/></div>
      </div>
      <div className="field-row">
        <div className="field">
          <label>Priority</label>
          <div className="chips"><span className="chip">low</span><span className="chip active">med</span><span className="chip">high</span></div>
        </div>
        <div className="field">
          <label>Recurring</label>
          <select><option>—</option><option>Daily</option><option>Every 2 days</option><option>Weekly</option><option>Monthly</option></select>
        </div>
      </div>
      <div className="field">
        <label>Room</label>
        <select>{ROOMS.map(r => <option key={r.id}>{r.name}</option>)}</select>
      </div>
      <div className="field">
        <label>Related plants / equipment</label>
        <input placeholder="WC-1, WC-2 · or e.g. Levoit 300S"/>
      </div>
      <div className="field"><label>Notes</label><textarea placeholder="What needs to happen, what to bring, where to look…"/></div>
    </div>
  );
};

const EquipForm = () => {
  const { ROOMS } = window.GFData;
  return (
    <div>
      <div className="field"><label>Name</label><input placeholder="e.g. AC Infinity Cloudline T6"/></div>
      <div className="field-row">
        <div className="field">
          <label>Category</label>
          <select><option>Lights</option><option>Inline Fan</option><option>Clip Fans</option><option>Humidifier</option><option>Dehumidifier</option><option>Heater</option><option>Sensors</option><option>Cameras</option><option>Controller</option><option>Tent</option><option>Nutrients</option><option>Misc Tools</option></select>
        </div>
        <div className="field">
          <label>Room</label>
          <select><option>—</option>{ROOMS.map(r => <option key={r.id}>{r.name}</option>)}</select>
        </div>
      </div>
      <div className="field-row">
        <div className="field"><label>Mode / setting</label><input placeholder="e.g. Auto · 65%"/></div>
        <div className="field"><label>Power draw (W)</label><input placeholder="e.g. 211"/></div>
      </div>
      <div className="field">
        <label>Status</label>
        <div className="chips"><span className="chip active">Online</span><span className="chip">Attention</span><span className="chip">Critical</span><span className="chip">Offline</span></div>
      </div>
      <div className="field"><label>Maintenance schedule</label><select><option>—</option><option>Monthly</option><option>Every 3 months</option><option>Per cycle</option></select></div>
      <div className="field"><label>Notes</label><textarea placeholder="Firmware, serial, purchase date, calibration notes…"/></div>
    </div>
  );
};

window.GFModal = Modal;
