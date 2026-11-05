import { useEffect, useState } from "react";
import { PALETTES, deviceVoices } from "../lib/settings";

// Rule 7 and 15: the person changes how it looks and decides support person and sharing.
export default function SettingsScreen({ settings, update, onBack }) {
  const choice = (label, key, options) => (
    <>
      <label htmlFor={key}>{label}</label>
      <select id={key} value={settings[key]} onChange={(e) => update({ [key]: e.target.value })}>
        {options.map(([v, t]) => <option key={v} value={v}>{t}</option>)}
      </select>
    </>
  );
  // Voices on the device load a moment after the page does.
  const [voices, setVoices] = useState(deviceVoices);
  useEffect(() => {
    if (!("speechSynthesis" in window)) return undefined;
    const update = () => setVoices(deviceVoices());
    window.speechSynthesis.addEventListener("voiceschanged", update);
    return () => window.speechSynthesis.removeEventListener("voiceschanged", update);
  }, []);

  const toggle = (label, key) => (
    <label className="check">
      <input type="checkbox" checked={settings[key]} onChange={(e) => update({ [key]: e.target.checked })} />
      {label}
    </label>
  );

  return (
    <section>
      <h1>Settings</h1>

      <div className="card">
        <h2>How it looks</h2>
        {choice("Text size", "textSize", [["medium", "Medium"], ["large", "Large"], ["larger", "Larger"]])}
        {choice("Font", "font", [["sans", "Plain"], ["serif", "Serif"], ["verdana", "Wide letters"]])}
        <fieldset style={{ border: 0, padding: 0, margin: "0.75rem 0 0" }}>
          <legend>Colors</legend>
          {PALETTES.map((p) => (
            <label key={p.id} className="palette">
              <input type="radio" name="theme" value={p.id}
                checked={settings.theme === p.id} onChange={() => update({ theme: p.id })} />
              <span className="swatch" aria-hidden="true">
                <span style={{ background: p.bg }} /><span style={{ background: p.panel }} /><span style={{ background: p.accent }} />
              </span>
              {p.name}
            </label>
          ))}
        </fieldset>
        {toggle("Show pictures", "pictures")}
      </div>

      <div className="card">
        <h2>Reading and praise</h2>
        {toggle("Read aloud", "readAloud")}
        {settings.readAloud && (
          <>
            <label htmlFor="voiceName">Voice (from your device)</label>
            <select id="voiceName" value={settings.voiceName} onChange={(e) => update({ voiceName: e.target.value })}>
              <option value="">Default voice</option>
              {voices.map((v) => <option key={v.name} value={v.name}>{v.name}</option>)}
            </select>
            {choice("Speed", "voiceSpeed", [["slow", "Slow"], ["normal", "Normal"]])}
          </>
        )}
        {choice("Praise", "praise", [["calm", "Calm"], ["cheerful", "Cheerful"], ["off", "Off"]])}
      </div>

      <div className="card">
        <h2>Game and sounds</h2>
        {choice("Style", "style", [["normal", "Normal"], ["game", "Game"]])}
        {choice("Sound volume", "sound", [["off", "Off"], ["very_soft", "Very soft"], ["soft", "Soft"], ["normal", "Normal"]])}
        {settings.style === "game" && (
          <>
            {choice("Sound type", "soundType", [["chime", "Chime"], ["nature", "Nature"], ["theme", "Theme"]])}
            {choice("Animations", "animations", [["off", "Off"], ["calm", "Calm"], ["lively", "Lively"]])}
            {toggle("Surprise me (hide the next area until it opens)", "surpriseMe")}
          </>
        )}
        {choice("Which hand do you use most?", "hand", [["right", "Right"], ["left", "Left"], ["both", "Both"]])}
        <button className="btn" onClick={() => { update({ setupDone: false }); onBack(); }}>
          Redo first-time setup
        </button>
      </div>

      <div className="card">
        <h2>Help from people</h2>
        <label htmlFor="support">Who do you want to ask for help?</label>
        <input id="support" type="text" value={settings.supportPerson}
          onChange={(e) => update({ supportPerson: e.target.value })} />
        {toggle("Share a summary with staff", "shareWithStaff")}
        <p className="muted">This is off unless you turn it on.</p>
        {choice("Phone type (for paying by phone)", "phoneType", [
          ["iphone_face_id", "iPhone with Face ID"],
          ["iphone_home_button", "iPhone with a home button"],
          ["android", "Android"],
        ])}
      </div>

      <div className="card">
        <h2>Who is using this</h2>
        <label htmlFor="person">Name or ID</label>
        <input id="person" type="text" value={settings.personId}
          onChange={(e) => update({ personId: e.target.value.trim() })} />
        <label htmlFor="week">Week</label>
        <input id="week" type="number" min="1" value={settings.week}
          onChange={(e) => update({ week: Number(e.target.value) || 1 })} />
      </div>

      <button className="btn primary" onClick={onBack}>Back</button>
    </section>
  );
}
