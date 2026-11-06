import { useEffect, useRef, useState } from "react";
import AskForHelp from "../components/AskForHelp/AskForHelp";
import "./resident.css";
import { getTasks, getToday, logEvent, sessionId } from "../lib/api";
import { BottomNav, TopBar } from "./NavBars";
import { Icon } from "../lib/icons";
import { clearSession, loadSession, saveSession } from "../lib/session";
import { PALETTES, askedAboutSkips, firstOpenDone, fromUrl, lookAttributes, markAskedAboutSkips, markFirstOpenDone, speak, supportName, useSettings } from "../lib/settings";
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
import HowGameWorks from "./HowGameWorks";
import { resolveWorld } from "../lib/worlds";
import GameBackdrop from "./Backdrops";
import ChooseWorld from "./ChooseWorld";
import ProfileScreen from "./ProfileScreen";
import SplashScreen from "./SplashScreen";
import VoiceAgent from "../components/VoiceAgent/VoiceAgent";

// One screen at a time. All step text and help levels come from /today (Format 3).
export default function ResidentApp() {
  const [settings, update] = useSettings();
  const [urlPatch] = useState(fromUrl);
  const s = { ...settings, ...urlPatch };
  // Remember the person and week from the address, so the nav's plain /resident link still works.
  useEffect(() => { if (Object.keys(urlPatch).length) update(urlPatch); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const rootRef = useRef(null);
  const [setupBack, setSetupBack] = useState(null); // Back inside first-time setup (previous question)
  // The logo screen shows once each time the app is opened.
  const [splash, setSplash] = useState(() => { try { return sessionStorage.getItem("carryover.splash") !== "1"; } catch { return true; } });
  const [noAuto, setNoAuto] = useState(false);
  const closeSplash = () => { setNoAuto(false); try { sessionStorage.setItem("carryover.splash", "1"); } catch { /* ignore */ } setSplash(false); };
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
  const [splitToken, setSplitToken] = useState(0); // "Show the small steps" from the Help screen
  const [tasksLoaded, setTasksLoaded] = useState(false);

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

  // Home: the Carryover first page. Continue then starts the first-time steps again.
  function goHome() {
    window.speechSynthesis?.cancel();
    setInTask(false);
    update({ setupDone: false });
    setView("tasks");
    setNoAuto(true);
    try { sessionStorage.removeItem("carryover.splash"); } catch { /* ignore */ }
    setSplash(true);
  }


  // Top bar: "← Back" on every screen except My tasks and setup.
  const inSetup = view === "tasks" && ready && !s.setupDone;
  const back = {
    tasks: inSetup ? setupBack : null,
    world: () => setView("tasks"),
    chooseworld: () => setView("tasks"),
    profile: () => setView("tasks"),
    settings: () => setView(returnTo === "step" || inTask ? returnTo : "tasks"),
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
  const names = { tasks: inSetup ? "Welcome" : "My tasks", world: "My world", chooseworld: "Choose your world", profile: "Profile", settings: "Settings", help: "Help", all: "All steps", break: "Take a break" };
  const title = names[view] || (today ? today.title : "Carryover");
  // During a task, Settings is a gear at the top right (the bottom bar is hidden then).
  const taskViews = ["start", "firstopen", "safety", "skillcard", "step", "help", "all", "break", "done"];
  const gear = taskViews.includes(view) ? (
    <button className="icon-btn" onClick={() => { setReturnTo(view); setView("settings"); }} aria-label="Settings" data-tip="Settings">
      <Icon.settings />
    </button>
  ) : null;
  // The profile circle sits at the top right of the top-level screens.
  const profileCircle = ["tasks", "world"].includes(view) && ready && s.setupDone ? (
    <button className="avatar-btn" onClick={() => setView("profile")} aria-label="Profile">
      <span aria-hidden="true">{(s.personId || "?").charAt(0).toUpperCase()}</span>
    </button>
  ) : null;
  // Voice helper: the same actions the buttons do. It takes the person to where the action
  // needs to be, then does it, and says what it did in plain words.
  function runCommand(action, arg) {
    const noTask = { ok: false, say: "No task is open yet. Say the name of a task, like open heat a meal." };
    const inStep = inTask && step;
    const send = (name, say) => {
      const go = () => window.dispatchEvent(new CustomEvent("carryover:voice", { detail: { action: name } }));
      if (view === "step") go(); else { setView("step"); setTimeout(go, 300); }
      return { ok: true, say };
    };
    // On the first page the only thing to do is Continue.
    if (splash) {
      if (action === "play" || action === "start") { closeSplash(); return { ok: true, say: "Continuing." }; }
      return { ok: false, say: "Say continue to begin." };
    }
    if (view === "done" && ["prepareDone", "doneConfirmed", "start", "play", "tasks", "openTask"].includes(action) && action !== "openTask") {
      setView("tasks");
      return { ok: true, say: "Here are your tasks." };
    }
    switch (action) {
      case "prepareDone":
        if (view === "step") return { ok: true };
        if (inStep) { setView("step"); return { ok: true }; }
        return noTask;
      case "doneConfirmed": return inStep ? send("done", "Great. Moving on.") : noTask;
      case "replay": return inStep ? send("replay", "Reading it again.") : noTask;
      case "pause": return inStep ? send("pause", "Paused.") : noTask;
      case "play":
        if (view === "break") { resume(); return { ok: true, say: "Going back to your step." }; }
        return inStep ? send("play", "Reading.") : noTask;
      case "smallSteps":
      case "nextSmall": return inStep ? send("smallSteps", "Showing the small steps.") : noTask;
      case "help":
        if (view === "help") return { ok: true, say: "You are on the help page." };
        return inStep ? send("help", "Opening help.") : noTask;
      case "break":
        if (!inStep) return noTask;
        takeBreak();
        return { ok: true, say: "Taking a break. Your place is saved." };
      case "home": goHome(); return { ok: true, say: "Going to the first page." };
      case "tasks": setView("tasks"); return { ok: true, say: "Here are your tasks." };
      case "settings": setReturnTo(view); setView("settings"); return { ok: true, say: "Opening settings." };
      case "back":
        if (back) { back(); return { ok: true, say: "Going back." }; }
        return { ok: true, say: "You are at the start of this part." };
      case "allsteps":
        if (inStep) { setView("all"); return { ok: true, say: "Here are all the steps." }; }
        return noTask;
      case "start":
        if (view === "start" && today) { startTask(0); return { ok: true, say: "Starting." }; }
        if (view === "tasks" && ready && s.setupDone) return { ok: false, say: "Say the name of a task, like open heat a meal." };
        return { ok: false, say: "Choose an option, or say next." };
      case "openTask":
        if (!ready || !s.setupDone) return { ok: false, say: "Choose your options first. You can say sky, animals or space, then next." };
        if (inTask) setInTask(false);
        openTask(arg);
        return { ok: true, say: `Opening ${titles[arg] || "the task"}.` };
      default: return { ok: false, say: "I did not catch that." };
    }
  }
  const voiceUi = <VoiceAgent settings={s} view={view} tasks={taskIds.map((id) => ({ id, title: titles[id] || id }))} onCommand={runCommand} />;
  const showBottomNav = ready && s.setupDone && ["tasks", "world", "settings"].includes(view);
  const dark = (s.theme === "dark" ? "dark" : s.mode) === "dark";
  const world = resolveWorld(s);

  // Every new page starts at the top, not where the last one was scrolled to.
  useEffect(() => {
    if (rootRef.current) rootRef.current.scrollTop = 0;
    window.scrollTo(0, 0);
  }, [view]);

  if (splash) {
    return (
      <div className="resident splash-page" {...lookAttributes({ ...s, theme: s.theme })}>
        <SplashScreen onDone={closeSplash} autoAdvance={false} />
        <div className="splash-voice">
          <VoiceAgent settings={s} view="splash" tasks={[]} onCommand={runCommand} />
        </div>
      </div>
    );
  }

  return (
    <div ref={rootRef} className={`resident ${showBottomNav ? "has-bottom-nav" : ""} ${s.style === "game" ? "game" : ""}`} {...lookAttributes(s)}>
      {s.style === "game" && <GameBackdrop world={world} dark={dark} animations={s.animations} />}
      <TopBar title={title} onBack={back} onHome={goHome} right={<>{voiceUi}{gear || profileCircle}</>} />

      {error && <div className="card status" role="alert"><p>{error}</p></div>}

      {view === "settings" && (
        <SettingsScreen
          settings={s}
          update={update}
          onRedoSetup={() => { update({ setupDone: false }); setInTask(false); setView("tasks"); }}
        />
      )}

      {view !== "settings" && !ready && (
        <div className="card">
          <p>Open Settings and enter who is using Carryover.</p>
        </div>
      )}

      {view === "tasks" && ready && !s.setupDone && <SetupScreen update={update} setBack={setSetupBack} />}

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
          onResume={resume}
          game={s.style === "game" ? <HowGameWorks world={world} every={2} /> : null}
          chooseWorld={s.style === "game" && !s.gameWorld ? () => setView("chooseworld") : null} />
      )}

      {view === "start" && today && (
        <StartScreen
          today={today}
          onStart={() => startTask(0)}
          onLook={() => { log("show_all_pressed"); setView("all"); }}
          onRefresherAnswer={(a) => log("refresher_answer", { answer: a })}
          onBack={closeWithoutStart}
          askAboutSkips={Boolean(today.ask_about_skips) && !askedAboutSkips(personId, today.task_id)}
          onSkipAnswer={(a) => { markAskedAboutSkips(personId, today.task_id); log("still_want_answer", { answer: a }); }}
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
            paused={view !== "step"}
            praiseLine={praiseLine}
            awayNote={awayNote}
            log={log}
            onDone={finishStep}
            onBreak={takeBreak}
            onHelp={() => setView("help")}
            onSpeak={(t, handlers) => speak(t, s, handlers)}
            splitToken={splitToken}
            onSeeAll={() => { log("show_all_pressed", { step_id: step.step_id }); setView("all"); }}
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
              supportName={supportName(s)}
            />
          }
        />
      )}

      {view === "profile" && <ProfileScreen settings={s} />}

      {view === "chooseworld" && (
        <ChooseWorld settings={s} update={update} onDone={() => setView("tasks")} />
      )}

      {view === "world" && ready && (
        <GameWorld personId={personId} settings={s} update={update} world={world} />
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

      {view === "break" && today && (
        <BreakScreen step={step} settings={s} onResume={resume} onHome={() => setView("tasks")} />
      )}

      {view === "done" && today && (
        <DoneScreen today={today} settings={s} update={update} personId={personId} donePromise={donePromise}
          onFinish={() => setView("tasks")} log={log} world={world} />
      )}
      {showBottomNav && (
        <BottomNav current={view} showWorld={s.style === "game"}
          onTasks={() => setView("tasks")} onWorld={() => setView("world")} onSettings={() => setView("settings")} />
      )}
    </div>
  );
}
