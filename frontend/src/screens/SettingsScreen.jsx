import { useEffect, useState } from "react";
import { PALETTES, deviceVoices } from "../lib/settings";
import { WORLD_CHOICES } from "../lib/worlds";

// Settings (Carryover decisions): Looks, Reading voice, Game or Normal, Sound, Animations,
// Support person, Sharing with staff, Phone type, Redo first-time setup. Labels sit above
// every field. Only destructive actions ask "Are you sure?" (redo setup, turning sharing off).
export default function SettingsScreen({ settings, update, onRedoSetup }) {
  const [voices, setVoices] = useState(deviceVoices);
  const [confirm, setConfirm] = useState(null); // "redo" | "sharing"

  // Voices on the device load a moment after the page does.
  useEffect(() => {
    if (!("speechSynthesis" in window)) return undefined;
    const onChange = () => setVoices(deviceVoices());
    window.speechSynthesis.addEventListener("voiceschanged", onChange);
    return () => window.speechSynthesis.removeEventListener("voiceschanged", onChange);
  }, []);

  const choice = (label, key, options) => (
    <>
      <label htmlFor={key}>{label}</label>
      <select id={key} value={settings[key]} onChange={(e) => update({ [key]: e.target.value })}>
        {options.map(([v, t]) => <option key={v} value={v}>{t}</option>)}
      </select>
    </>
  );
  const radios = (legend, key, options) => (
    <fieldset>
      <legend>{legend}</legend>
      <div className="segmented">
        {options.map(([v, t]) => (
          <label key={v} className={`segment ${settings[key] === v ? "on" : ""}`}>
            <input type="radio" name={key} value={v} checked={settings[key] === v} onChange={() => update({ [key]: v })} />
            {t}
          </label>
        ))}
      </div>
    </fieldset>
  );
  const toggle = (label, key, onChange) => (
    <label className="check">
      <input type="checkbox" checked={Boolean(settings[key])}
        onChange={(e) => (onChange ? onChange(e.target.checked) : update({ [key]: e.target.checked }))} />
      {label}
    </label>
  );
  const sure = (text, yes, onYes) => (
    <div className="card status" role="alert">
      <p>{text}</p>
      <div className="row">
        <button className="btn primary" onClick={() => { setConfirm(null); onYes(); }}>{yes}</button>
        <button className="btn" onClick={() => setConfirm(null)}>Cancel</button>
      </div>
    </div>
  );
  const week = Number(settings.week);

  return (
    <section>
      <div className="card">
        <h2>Looks</h2>
        {choice("Text size", "textSize", [["medium", "Medium"], ["large", "Large"], ["larger", "Larger"]])}
        {choice("Font", "font", [["sans", "Plain"], ["serif", "Serif"], ["verdana", "Wide letters"]])}
        <fieldset>
          <legend>Colours</legend>
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
        {radios("Light or dark", "mode", [["light", "Light"], ["dark", "Dark"]])}
        {toggle("Show pictures", "pictures")}
      </div>

      <div className="card">
        <h2>Reading voice</h2>
        {toggle("Read steps aloud", "readAloud")}
        <label htmlFor="voiceName">Voice (from your phone)</label>
        <select id="voiceName" value={settings.voiceName} onChange={(e) => update({ voiceName: e.target.value })}>
          <option value="">Phone's default voice</option>
          {voices.map((v) => <option key={v.name} value={v.name}>{v.name}</option>)}
        </select>
        {radios("Speed", "voiceSpeed", [["slow", "Slow"], ["normal", "Normal"]])}
      </div>

      <div className="card">
        <h2>Game or Normal</h2>
        {radios("Style", "style", [["normal", "Normal"], ["game", "Game"]])}
        <p className="muted">Game: the whole app sits in a world you choose. Finish a task to pick a reward, and a new area opens every 2 tasks. Normal: no game at all.</p>
        {settings.style === "game" && (
          <>
            <label htmlFor="gameWorld">Game world</label>
            <select id="gameWorld" value={settings.gameWorld || "sky"} onChange={(e) => update({ gameWorld: e.target.value })}>
              {WORLD_CHOICES.map((w) => <option key={w.id} value={w.id}>{w.name}</option>)}
            </select>
            {WORLD_CHOICES.filter((w) => w.sub && w.id === (settings.gameWorld || "sky")).map((w) => (
              <div key={w.id}>
                <label htmlFor={w.sub}>{w.id === "animals" ? "Which animal" : "Which fruit"}</label>
                <select id={w.sub} value={settings[w.sub]} onChange={(e) => update({ [w.sub]: e.target.value })}>
                  {w.options.map(([v, t]) => <option key={v} value={v}>{t}</option>)}
                </select>
              </div>
            ))}
            {toggle("Surprise me (hide the next area until it opens)", "surpriseMe")}
          </>
        )}
      </div>

      <div className="card">
        <h2>Sound and animations</h2>
        {choice("Sound", "sound", [["off", "Off"], ["very_soft", "Very soft"], ["soft", "Soft"], ["normal", "Normal"]])}
        {settings.style === "game" && choice("Sound type", "soundType", [["chime", "Chime"], ["nature", "Nature"], ["theme", "Theme"]])}
        {choice("Animations", "animations", [["off", "Off"], ["calm", "Calm"], ["lively", "Lively"]])}
      </div>

      <div className="card">
        <h2>Support person</h2>
        <label htmlFor="support">Name</label>
        <input id="support" type="text" autoComplete="off" value={settings.supportPerson}
          onChange={(e) => update({ supportPerson: e.target.value })} />
        <p className="muted">If this is empty, buttons say "Ask staff".</p>
        <label htmlFor="supportContact">How to reach them</label>
        <input id="supportContact" type="text" autoComplete="off" value={settings.supportContact}
          onChange={(e) => update({ supportContact: e.target.value })} />
        <p className="muted">For example: "Call the front desk" or a phone number.</p>
      </div>

      <div className="card">
        <h2>Sharing with staff</h2>
        {toggle("Share a short summary with staff", "shareWithStaff",
          (on) => (on ? update({ shareWithStaff: true }) : setConfirm("sharing")))}
        <p className="muted">This is off unless you turn it on.</p>
        {confirm === "sharing" && sure("Stop sharing your summary with staff?", "Yes, stop sharing", () => update({ shareWithStaff: false }))}
      </div>

      <div className="card">
        <h2>Phone type</h2>
        {choice("For the steps about paying with your phone", "phoneType", [
          ["iphone_face_id", "iPhone with Face ID"],
          ["iphone_home_button", "iPhone with a home button"],
          ["android", "Android"],
        ])}
      </div>

      <div className="card">
        <h2>About you</h2>
        {choice("Which hand do you use most?", "hand", [["right", "Right"], ["left", "Left"], ["both", "Both"]])}
        <button className="btn" onClick={() => setConfirm("redo")}>Redo first-time setup</button>
        {confirm === "redo" && sure("Redo first-time setup? Your answers will be asked again.", "Yes, redo setup", onRedoSetup)}
      </div>

      <div className="card">
        <h2>For testing</h2>
        <label htmlFor="person">Who is using this (name or ID)</label>
        <input id="person" type="text" autoComplete="off" value={settings.personId}
          onChange={(e) => update({ personId: e.target.value.trim() })} aria-describedby="person-msg" />
        {!settings.personId && <p id="person-msg" className="field-error" role="alert">Enter a name or ID to see the tasks.</p>}
        {settings.style === "game" && (
          <>
            <p className="muted">Try Game mode without finishing real tasks. This only changes this phone, and is not logged.</p>
            <p>Pretend tasks done: {Number(settings.demoDone) || 0}</p>
            <div className="row">
              <button className="btn" onClick={() => update({ demoDone: (Number(settings.demoDone) || 0) + 1 })}>Pretend I finished a task</button>
              <button className="btn" onClick={() => update({ demoDone: 0, demoRewards: 0, gameItems: {} })}>Reset</button>
            </div>
            <button className="btn" onClick={() => update({ demoRewards: (Number(settings.demoRewards) || 0) + 10 })}>Pretend I earned 10 rewards</button>
          </>
        )}
        <label htmlFor="week">Week</label>
        <input id="week" type="number" inputMode="numeric" min="1" value={settings.week}
          onChange={(e) => update({ week: Math.max(1, Number(e.target.value) || 1) })} aria-describedby="week-msg" />
        {!(week >= 1) && <p id="week-msg" className="field-error" role="alert">The week must be 1 or more.</p>}
      </div>
    </section>
  );
}
