import { useEffect, useRef, useState } from "react";
import AskForHelp from "../components/AskForHelp/AskForHelp";
import "./resident.css";
import { getSetup, getTasks, getToday, logEvent, sessionId } from "../lib/api";
import Tip from "./Tip";
import { BottomNav, TopBar } from "./NavBars";
import { clearSession, loadSession, saveSession } from "../lib/session";
import { PALETTES, askedAboutSkips, firstOpenDone, fromUrl, lookAttributes, markAskedAboutSkips, markFirstOpenDone, speak, useSettings } from "../lib/settings";
import TaskList from "./TaskList";
import StartScreen from "./StartScreen";
import StepScreen from "./StepScreen";
import AllSteps from "./AllSteps";
import DoneScreen from "./DoneScreen";
import SettingsScreen from "./SettingsScreen";
import BreakScreen from "./BreakScreen";
import SetupScreen from "./SetupScreen";
import FirstOpen from "./FirstOpen";
import SafetyCard from "./SafetyCard";
import SkillCardScreen from "./SkillCardScreen";
import GameWorld from "./GameWorld";
import HelpScreen from "./HelpScreen";
import { worldFor } from "../lib/worlds";

// One screen at a time. All step text and help levels come from /today (Format 3).
export default function ResidentApp() {
  const [settings, update] = useSettings();
  const [urlPatch] = useState(fromUrl);
  const s = { ...settings, ...urlPatch };
  // Remember the person and week from the address, so the nav's plain /resident link still works.
  useEffect(() => { if (Object.keys(urlPatch).length) update(urlPatch); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const [view, setView] = useState("tasks");
  const [taskIds, setTaskIds] = useState([]);
  const [titles, setTitles] = useState({});
  const [today, setToday] = useState(null);
  const [index, setIndex] = useState(0);
  const [error, setError] = useState("");
  const [returnTo, setReturnTo] = useState("start");
  const startedRef = useRef(false); // true once the first step was started
  const [breakStartedAt, setBreakStartedAt] = useState(null);
  const [inTask, setInTask] = useState(false); // step screen stays mounted so the place and timing are kept
  const [praiseLine, setPraiseLine] = useState("");
  const [awayNote, setAwayNote] = useState(""); // task file break_note, after a long break
  const [pendingCards, setPendingCards] = useState([]); // skill cards to show before the next step
  const shownCards = useRef(new Set());
  const [donePromise, setDonePromise] = useState(null); // resolves when task_done is saved
  const [knownInterests, setKnownInterests] = useState([]); // from definitions.json, for Game mode
  const [previewTheme, setPreviewTheme] = useState(null); // colour being tried in the popup, not saved yet
  const [splitToken, setSplitToken] = useState(0); // "Show the small steps" from the Help screen
  const [tasksLoaded, setTasksLoaded] = useState(false);
  useEffect(() => {
    getSetup()
      .then((qs) => setKnownInterests((qs.find((q) => q.id === "interests") || { answers: [] }).answers))
      .catch(() => {});
  }, []);

  const personId = s.personId;
  const ready = Boolean(personId);

  // Load the task list and each task's title (titles come from the task files).
  useEffect(() => {
    if (!ready) return;
    setError("");
    getTasks()
      .then(async ({ tasks }) => {
        setTaskIds(tasks);
        const entries = await Promise.all(
          tasks.map((id) => getToday(personId, id, s.week).then((t) => [id, t.title]))
        );
        setTitles(Object.fromEntries(entries));
        setTasksLoaded(true);
      })
      .catch(() => { setError("Your tasks could not load. Check that the app is connected, then try again."); setTasksLoaded(true); });
  }, [personId, s.week, ready]);

  // Come back to the same step after leaving the tab or reloading.
  useEffect(() => {
    if (!ready) return;
    const saved = loadSession();
    if (!saved || saved.personId !== personId || saved.week !== s.week) return;
    getToday(personId, saved.taskId, s.week)
      .then((t) => {
        if (saved.index >= t.steps.length) { clearSession(); return; }
        startedRef.current = true;
        shownCards.current = new Set(saved.shownCards || []);
        setToday(t);
        setIndex(saved.index);
        setInTask(true);
        setView("step");
      })
      .catch(() => clearSession());
  }, [personId, s.week, ready]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (inTask && today) {
      saveSession({ personId, week: today.week, taskId: today.task_id, index, shownCards: [...shownCards.current] });
    } else if (!inTask && view !== "settings") {
      clearSession();
    }
  }, [inTask, today, index, view]); // eslint-disable-line react-hooks/exhaustive-deps

  const log = (event, extra = {}) =>
    today && logEvent({
      person_id: personId,
      task_id: today.task_id,
      session_id: sessionId(personId, today.task_id, today.week),
      week: today.week,
      event,
      ...extra,
    });

  async function openTask(taskId) {
    setError("");
    try {
      const t = await getToday(personId, taskId, s.week);
      startedRef.current = false;
      setToday(t);
      setIndex(0);
      setView(t.session_number === 1 && !firstOpenDone(personId, taskId) ? "firstopen" : "start");
      logEvent({
        person_id: personId, task_id: taskId, week: s.week,
        session_id: sessionId(personId, taskId, s.week), event: "task_opened",
      });
    } catch (e) {
      setError(e.message);
    }
  }

  function closeWithoutStart() {
    if (!startedRef.current) log("task_closed_no_start");
    setInTask(false);
    setView("tasks");
  }

  // Go to a step. If today's view has a skill card for it that was not shown yet this
  // task, show the card first. Returns true when a card is showing.
  function enterStep(i, t = today) {
    setIndex(i);
    const cards = (t.skill_cards || []).filter(
      (c) => c.step_id === t.steps[i].step_id && c.card && !shownCards.current.has(`${c.skill_id}:${c.step_id}`)
    );
    if (!cards.length) return false;
    cards.forEach((c) => shownCards.current.add(`${c.skill_id}:${c.step_id}`));
    setPendingCards(cards);
    setView("skillcard");
    return true;
  }

  // Start at step `at` (0 unless they picked a step in All steps).
  const startAt = useRef(0);
  function startTask(at = 0) {
    startedRef.current = true;
    startAt.current = at;
    setAwayNote("");
    setInTask(true);
    setPraiseLine("");
    shownCards.current = new Set();
    setIndex(at);
    // The safety card shows first when today's view says it is the first time.
    if (today.show_safety_card && today.safety_card_content) {
      setView("safety");
    } else if (!enterStep(at)) {
      setView("step");
    }
  }

  function afterSafety() {
    if (!enterStep(startAt.current)) setView("step");
  }

  // All steps: tapping a step goes to it.
  function jumpTo(i) {
    if (!inTask) { startTask(i); return; }
    setPraiseLine("");
    setAwayNote("");
    if (!enterStep(i)) setView("step");
  }

  // Back on step 1 goes to the task start screen (Carryover decisions).
  function backToStart() {
    setInTask(false);
    setView("start");
  }

  function afterSkillCard() {
    const rest = pendingCards.slice(1);
    setPendingCards(rest);
    if (!rest.length) setView("step");
  }

  function takeBreak() {
    setBreakStartedAt(Date.now());
    log("paused", { step_id: today.steps[index].step_id });
    setView("break");
  }

  function resume() {
    const seconds = breakStartedAt ? Math.round((Date.now() - breakStartedAt) / 1000) : null;
    log("resumed", { step_id: today.steps[index].step_id, seconds });
    const note = today.break_note;
    setAwayNote(note && seconds !== null && seconds >= note.after_minutes * 60 ? note.text : "");
    setBreakStartedAt(null);
    setView("step");
  }

  function finishStep() {
    const n = today.steps[index].number;
    if (index + 1 >= today.steps.length) {
      setDonePromise(log("task_done"));
      setInTask(false);
      setView("done");
    } else {
      setPraiseLine(
        s.praise === "off" ? "" : s.praise === "cheerful" ? `Step ${n} done. Well done.` : `Step ${n} done.`
      );
      setAwayNote("");
      enterStep(index + 1);
    }
  }

  function goBackOneStep() {
    // "Tapped Done by mistake? Go back": the step just finished is the one undone.
    log("step_done_undone", { step_id: today.steps[index - 1].step_id });
    setPraiseLine("");
    setAwayNote("");
    setIndex(Math.max(0, index - 1));
  }

  const step = today && today.steps[index];

  // One-time questions, each asked once, in the moment.
  const showReadTip = view === "step" && inTask && !s.tipReadAsked && !s.readAloud;
  const showColorTip = view === "start" && !s.tipColorAsked;

  // Top bar: "← Back" on every screen except My tasks and setup.
  const inSetup = view === "tasks" && ready && !s.setupDone;
  const back = {
    world: () => setView("tasks"),
    settings: () => setView("tasks"),
    start: closeWithoutStart,
    firstopen: closeWithoutStart,
    all: () => setView(inTask ? "step" : "start"),
    safety: backToStart,
    skillcard: backToStart,
    step: index > 0 ? goBackOneStep : backToStart,
    help: () => setView("step"),
    break: resume,
    done: () => setView("tasks"),
  }[view] || null;
  const names = { tasks: inSetup ? "Welcome" : "My tasks", world: "My world", settings: "Settings", help: "Help", all: "All steps", break: "Take a break" };
  const title = names[view] || (today ? today.title : "Carryover");
  const allStepsLink = view === "step" ? (
    <button className="navbtn" onClick={() => { log("show_all_pressed", { step_id: step.step_id }); setView("all"); }}>All steps</button>
  ) : null;
  const showBottomNav = ready && s.setupDone && ["tasks", "world", "settings"].includes(view);
  const dark = (s.theme === "dark" ? "dark" : s.mode) === "dark";
  const world = worldFor(s.interests, knownInterests);

  return (
    <div className={`resident ${showBottomNav ? "has-bottom-nav" : ""}`} {...lookAttributes({ ...s, theme: previewTheme || s.theme })}>
      <TopBar title={title} onBack={back} right={allStepsLink} />

      {error && <div className="card status" role="alert"><p>{error}</p></div>}

      {view === "settings" && (
        <SettingsScreen
          settings={s}
          update={update}
          onRedoSetup={() => { update({ setupDone: false }); setInTask(false); setView("tasks"); }}
          previewTheme={previewTheme}
        />
      )}

      {view !== "settings" && !ready && (
        <div className="card">
          <p>Open Settings and enter who is using Carryover.</p>
        </div>
      )}

      {view === "tasks" && ready && !s.setupDone && <SetupScreen update={update} />}

      {view === "firstopen" && today && (
        <FirstOpen
          today={today}
          log={log}
          onDone={() => { markFirstOpenDone(personId, today.task_id); setView("start"); }}
        />
      )}

      {view === "tasks" && ready && s.setupDone && (
        <TaskList taskIds={taskIds} titles={titles} onOpen={openTask} loaded={tasksLoaded}
          resume={inTask && step ? { title: today.title, number: step.number } : null}
          onResume={resume} />
      )}

      {view === "start" && today && (
        <StartScreen
          today={today}
          onStart={() => startTask(0)}
          onLook={() => { log("show_all_pressed"); setView("all"); }}
          onRefresherAnswer={(a) => log("refresher_answer", { answer: a })}
          onBack={closeWithoutStart}
          askAboutSkips={Boolean(today.ask_about_skips) && !askedAboutSkips(personId, today.task_id)}
          onSkipAnswer={(a) => { markAskedAboutSkips(personId, today.task_id); log("end_question", { answer: a }); }}
        />
      )}

      {view === "all" && today && (
        <AllSteps today={today} inTask={inTask} currentIndex={index} onJump={jumpTo}
          onStart={() => startTask(0)} onBack={() => setView("step")} />
      )}

      {inTask && step && (
        <div hidden={view !== "step"}>
          <StepScreen
            key={step.step_id}
            step={step}
            settings={s}
            paused={view !== "step" || showReadTip}
            praiseLine={praiseLine}
            awayNote={awayNote}
            log={log}
            onDone={finishStep}
            onBreak={takeBreak}
            onHelp={() => setView("help")}
            onSpeak={(t) => speak(t, s)}
            splitToken={splitToken}
          />
        </div>
      )}

      {view === "help" && step && (
        <HelpScreen
          step={step}
          settings={s}
          canShowSmall={step.substeps.length > 0}
          onShowSmall={() => { setSplitToken((n) => n + 1); setView("step"); }}
          onBack={() => setView("step")}
          stuckPanel={
            <AskForHelp
              personId={personId}
              taskId={today.task_id}
              stepId={step.step_id}
              week={today.week}
              sessionId={sessionId(personId, today.task_id, today.week)}
              autoRead={s.readAloud}
            />
          }
        />
      )}

      {view === "world" && ready && (
        <GameWorld personId={personId} settings={s} update={update} dark={dark} world={world} />
      )}

      {view === "safety" && today && (
        <SafetyCard content={today.safety_card_content} onContinue={afterSafety} />
      )}

      {view === "skillcard" && today && pendingCards[0] && (
        <SkillCardScreen
          key={pendingCards[0].skill_id + pendingCards[0].step_id}
          entry={pendingCards[0]}
          settings={s}
          log={log}
          onContinue={afterSkillCard}
        />
      )}

      {showReadTip && (
        <Tip
          title="Want the steps read to you?"
          yesLabel="Yes, try it"
          noLabel="Not now"
          onYes={() => update({ readAloud: true, tipReadAsked: true })}
          onNo={() => update({ tipReadAsked: true })}
        >
          <p className="muted">You can change this any time in Settings.</p>
        </Tip>
      )}

      {showColorTip && (
        // Tapping a colour only shows it. Nothing is saved until they press "Use this one".
        <Tip
          title="Want a different color look?"
          yesLabel={previewTheme ? "Use this one" : null}
          onYes={() => { update({ theme: previewTheme, tipColorAsked: true }); setPreviewTheme(null); }}
          noLabel={previewTheme ? "Keep my old one" : "Keep this one"}
          onNo={() => { setPreviewTheme(null); update({ tipColorAsked: true }); }}
        >
          <p className="muted">Tap one to see how it looks.</p>
          {PALETTES.map((p) => {
            const on = (previewTheme || s.theme) === p.id;
            return (
              <button key={p.id} className={`btn palette-choice ${on ? "on" : ""}`} aria-pressed={on} onClick={() => setPreviewTheme(p.id)}>
                <span className="swatch" aria-hidden="true">
                  <span style={{ background: p.bg }} /><span style={{ background: p.panel }} /><span style={{ background: p.accent }} />
                </span>
                {p.name}{on ? " (showing now)" : ""}
              </button>
            );
          })}
          <p className="muted">You can change this any time in Settings.</p>
        </Tip>
      )}

      {view === "break" && today && (
        <BreakScreen step={step} settings={s} onResume={resume} onHome={() => setView("tasks")} />
      )}

      {view === "done" && today && (
        <DoneScreen today={today} settings={s} update={update} personId={personId} donePromise={donePromise}
          onFinish={() => setView("tasks")} log={log} dark={dark} world={world} />
      )}
      {showBottomNav && (
        <BottomNav current={view} showWorld={s.style === "game"}
          onTasks={() => setView("tasks")} onWorld={() => setView("world")} onSettings={() => setView("settings")} />
      )}
    </div>
  );
}
