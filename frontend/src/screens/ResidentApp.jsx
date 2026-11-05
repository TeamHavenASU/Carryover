import { useEffect, useRef, useState } from "react";
import AskForHelp from "../components/AskForHelp/AskForHelp";
import "./resident.css";
import { getTasks, getToday, logEvent, sessionId } from "../lib/api";
import { askedAboutSkips, firstOpenDone, fromUrl, lookAttributes, markAskedAboutSkips, markFirstOpenDone, speak, useSettings } from "../lib/settings";
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
      })
      .catch((e) => setError(e.message));
  }, [personId, s.week, ready]);

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

  function startTask() {
    startedRef.current = true;
    setAwayNote("");
    setInTask(true);
    setPraiseLine("");
    shownCards.current = new Set();
    setIndex(0);
    // The safety card shows first when today's view says it is the first time.
    if (today.show_safety_card && today.safety_card_content) {
      setView("safety");
    } else if (!enterStep(0)) {
      setView("step");
    }
  }

  function afterSafety() {
    if (!enterStep(0)) setView("step");
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

  return (
    <div className="resident" {...lookAttributes(s)}>
      <div className="topbar">
        <strong>Carryover</strong>
        {view !== "settings" && (
          <button className="btn link" onClick={() => { setReturnTo(view); setView("settings"); }}>
            Settings
          </button>
        )}
      </div>

      {error && <div className="card status" role="alert">{error}</div>}

      {view === "settings" && (
        <SettingsScreen
          settings={s}
          update={update}
          onBack={() => setView(ready ? returnTo : "tasks")}
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
        <TaskList taskIds={taskIds} titles={titles} onOpen={openTask} showWorld={s.style === "game"} onWorld={() => setView("world")} />
      )}

      {view === "start" && today && (
        <StartScreen
          today={today}
          onStart={startTask}
          onLook={() => { log("show_all_pressed"); setReturnTo("start"); setView("all"); }}
          onRefresherAnswer={(a) => log("refresher_answer", { answer: a })}
          onBack={closeWithoutStart}
          askAboutSkips={Boolean(today.ask_about_skips) && !askedAboutSkips(personId, today.task_id)}
          onSkipAnswer={(a) => { markAskedAboutSkips(personId, today.task_id); log("end_question", { answer: a }); }}
        />
      )}

      {view === "all" && today && (
        <AllSteps today={today} inTask={inTask} onStart={startTask} onBack={() => setView(returnTo === "step" ? "step" : "start")} />
      )}

      {inTask && step && (
        <div hidden={view !== "step"}>
          <StepScreen
            key={step.step_id}
            step={step}
            today={today}
            settings={s}
            index={index}
            paused={view !== "step"}
            praiseLine={praiseLine}
            awayNote={awayNote}
            log={log}
            onDone={finishStep}
            onBackStep={goBackOneStep}
            onBreak={takeBreak}
            onSeeAll={() => { log("show_all_pressed", { step_id: step.step_id }); setReturnTo("step"); setView("all"); }}
            onSpeak={(t) => speak(t, s)}
          />
          <AskForHelp
            personId={personId}
            taskId={today.task_id}
            stepId={step.step_id}
            week={today.week}
            sessionId={sessionId(personId, today.task_id, today.week)}
            autoRead={s.readAloud}
          />
        </div>
      )}

      {view === "world" && ready && (
        <GameWorld personId={personId} settings={s} onBack={() => setView("tasks")} />
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
        <BreakScreen today={today} step={step} onResume={resume} />
      )}

      {view === "done" && today && (
        <DoneScreen today={today} settings={s} update={update} personId={personId} donePromise={donePromise} onFinish={() => setView("tasks")} log={log} />
      )}
    </div>
  );
}
