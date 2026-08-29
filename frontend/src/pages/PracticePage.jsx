import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import TopBar from "../components/TopBar";
import Mascot from "../components/Mascot";
import ConfettiBurst from "../components/ConfettiBurst";
import ScreenBackground from "../components/ScreenBackground";
import { useAuth } from "../context/AuthContext";
import { TOPIC_LABELS, levelLabel } from "../constants";
import {
  getQuestions,
  generateQuestions,
  getSolution,
  recordAttempt,
  apiErrorMessage,
} from "../api";

function capitalize(word) {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

function shuffle(items) {
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

function LevelBadge({ track, difficulty }) {
  return (
    <div className={`level-badge level-${difficulty}`}>
      {levelLabel(track, difficulty)}
    </div>
  );
}

export default function PracticePage() {
  const { track, topic, difficulty } = useParams();
  const navigate = useNavigate();
  const { activeChild, logoutChild, signOut } = useAuth();

  const [questions, setQuestions] = useState([]);
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState(null);
  const [solution, setSolution] = useState(null);
  const [loadingSolution, setLoadingSolution] = useState(false);
  const [loadingQuestions, setLoadingQuestions] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  // True until the first attempt is recorded for this level visit, so that
  // attempt is the one that starts a new PracticeSession (see attempt-history).
  const isFreshRound = useRef(true);

  const loadBankQuestions = useCallback(async () => {
    setLoadingQuestions(true);
    setError("");
    try {
      const qs = await getQuestions({ topic, track, difficulty });
      setQuestions(shuffle(qs));
      setIndex(0);
      setSelected(null);
      setSolution(null);
      isFreshRound.current = true;
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't load questions. Please try again."));
    } finally {
      setLoadingQuestions(false);
    }
  }, [topic, track, difficulty]);

  useEffect(() => {
    loadBankQuestions();
  }, [loadBankQuestions]);

  const loadMoreQuestions = useCallback(async () => {
    setGenerating(true);
    setError("");
    try {
      const qs = await generateQuestions({ topic, track, difficulty, n: 5 });
      setIndex(questions.length);
      setQuestions((prev) => [...prev, ...qs]);
      setSelected(null);
      setSolution(null);
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't create new questions. Please try again."));
    } finally {
      setGenerating(false);
    }
  }, [topic, track, difficulty, questions]);

  const current = questions[index];
  const isLastQuestion = index === questions.length - 1;
  const busy = loadingQuestions || generating;

  function handleSelect(option) {
    if (selected !== null || !current) return;
    setSelected(option);
    const isCorrect = option === current.correct_answer;
    recordAttempt(activeChild.token, activeChild.id, {
      topic,
      track,
      difficulty,
      question_id: current.id,
      selected_answer: option,
      is_correct: isCorrect,
      new_session: isFreshRound.current,
    }).catch(() => {
      // Progress syncing is best-effort — don't interrupt practice over it.
    });
    isFreshRound.current = false;
  }

  function handleNext() {
    setSelected(null);
    setSolution(null);
    setIndex((i) => i + 1);
  }

  async function handleShowSolution() {
    if (!current) return;
    setLoadingSolution(true);
    setError("");
    try {
      const data = await getSolution({
        question_text: current.question_text,
        correct_answer: current.correct_answer,
        explanation_hint: current.explanation_hint,
      });
      setSolution(data);
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't fetch a solution right now."));
    } finally {
      setLoadingSolution(false);
    }
  }

  const title = `${TOPIC_LABELS[topic] ?? capitalize(topic)} · ${capitalize(track)}`;

  function handleSwitchChild() {
    logoutChild();
    navigate("/children");
  }

  function handleSignOut() {
    signOut();
    navigate("/parent/auth");
  }

  return (
    <div className="app-frame">
      <ScreenBackground />
      <TopBar
        title={title}
        onBack={() => navigate(`/levels/${track}/${topic}`)}
        actions={[
          { label: "Switch", onClick: handleSwitchChild },
          { label: "Sign out", onClick: handleSignOut },
        ]}
      />
      <div className="screen">
        {loadingQuestions && (
          <>
            <Mascot state="encouraging" />
            <div className="loading-spinner" />
            <p className="subtitle">Getting your questions ready…</p>
          </>
        )}

        {generating && (
          <>
            <Mascot state="encouraging" />
            <div className="loading-spinner" />
            <p className="subtitle">
              Creating brand-new questions just for you… this can take a little while ⏳
            </p>
          </>
        )}

        {error && <div className="error-banner">{error}</div>}

        {!busy && !current && !error && (
          <>
            <Mascot state="encouraging" size="lg" />
            <p className="subtitle">
              No questions here yet — let's create some just for you!
            </p>
            <button
              type="button"
              className="btn btn-accent btn-block"
              onClick={loadMoreQuestions}
            >
              🌟 Generate Questions
            </button>
          </>
        )}

        {!busy && current && (
          <>
            <LevelBadge track={track} difficulty={difficulty} />

            <div className="question-card">
              <div className="question-text">{current.question_text}</div>
            </div>

            <div className="option-grid">
              {selected !== null && selected === current.correct_answer && (
                <ConfettiBurst key={current.id} />
              )}
              {current.options.map((option) => {
                let cls = "option-btn";
                if (selected !== null) {
                  if (option === current.correct_answer) cls += " correct";
                  else if (option === selected) cls += " wrong";
                }
                return (
                  <button
                    key={option}
                    type="button"
                    className={cls}
                    disabled={selected !== null}
                    onClick={() => handleSelect(option)}
                  >
                    {option}
                  </button>
                );
              })}
            </div>

            {selected !== null && (
              <div className={`feedback-banner ${selected === current.correct_answer ? "correct" : "wrong"}`}>
                <Mascot state={selected === current.correct_answer ? "happy" : "confused"} size="sm" />
                {selected === current.correct_answer ? "🎉 Correct! Great job!" : "Not quite — you can do it!"}
              </div>
            )}

            <button
              type="button"
              className="btn btn-outline btn-block"
              disabled={selected === null || loadingSolution}
              onClick={handleShowSolution}
            >
              {loadingSolution ? "Thinking…" : "🤔 Show me how"}
            </button>

            {solution && (
              <div className="solution-panel">
                <ol>
                  {solution.steps.map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
                <strong>Answer: {solution.final_answer}</strong>
                <span>{solution.encouragement}</span>
              </div>
            )}

            {selected !== null && !isLastQuestion && (
              <button type="button" className="btn btn-primary btn-block" onClick={handleNext}>
                Next Question ➡️
              </button>
            )}

            {selected !== null && isLastQuestion && (
              <button type="button" className="btn btn-accent btn-block" onClick={loadMoreQuestions}>
                🌟 Practice More
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
}
