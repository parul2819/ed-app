import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import TopBar from "../components/TopBar";
import Stars from "../components/Stars";
import ScreenBackground from "../components/ScreenBackground";
import { useAuth } from "../context/AuthContext";
import { getPassage, getPassages, recordAttempt, apiErrorMessage } from "../api";

// The sole topic/track pairing for subject="english" — see the note on
// `Topic` in schemas.py for why these two values are fixed.
const ENGLISH_TOPIC = "comprehension";
const ENGLISH_TRACK = "school";

// Mirrors config.py's STAR_THRESHOLD_1/2/3 defaults — the backend has no
// endpoint exposing these, so the completion screen keeps its own copy to
// score a session immediately, without waiting on a server round trip.
const STAR_THRESHOLD_3 = 90;
const STAR_THRESHOLD_2 = 70;
const STAR_THRESHOLD_1 = 50;

function starsForAccuracy(accuracy) {
  if (accuracy >= STAR_THRESHOLD_3) return 3;
  if (accuracy >= STAR_THRESHOLD_2) return 2;
  if (accuracy >= STAR_THRESHOLD_1) return 1;
  return 0;
}

function encouragementForAccuracy(accuracy) {
  if (accuracy >= STAR_THRESHOLD_3) return "🌟 Amazing! You're a reading star!";
  if (accuracy >= STAR_THRESHOLD_2) return "🎉 Great job! Keep it up!";
  if (accuracy >= STAR_THRESHOLD_1) return "👍 Good effort! Practice makes perfect.";
  return "💪 Keep trying — you'll get better each time!";
}

export default function PassagePage() {
  const { passageId } = useParams();
  const navigate = useNavigate();
  const { activeChild } = useAuth();
  const [passage, setPassage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [showSummary, setShowSummary] = useState(false);
  const [allPassages, setAllPassages] = useState([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError("");
      setIndex(0);
      setSelected(null);
      setCorrectCount(0);
      setShowSummary(false);
      try {
        const data = await getPassage(passageId);
        if (!cancelled) setPassage(data);
      } catch (err) {
        if (!cancelled) setError(apiErrorMessage(err, "Couldn't load this passage."));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [passageId]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await getPassages();
        if (!cancelled) setAllPassages(data);
      } catch {
        // Prev/Next navigation is a convenience — losing it silently on
        // failure is fine, the passage list page still works as a fallback.
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const ladderIndex = allPassages.findIndex((p) => p.id === passageId);
  const prevPassage = ladderIndex > 0 ? allPassages[ladderIndex - 1] : null;
  const nextPassage =
    ladderIndex >= 0 && ladderIndex < allPassages.length - 1
      ? allPassages[ladderIndex + 1]
      : null;

  function handleSelect(option) {
    if (selected !== null || !question) return;
    setSelected(option);
    const isCorrect = option === question.correct_answer;
    if (isCorrect) setCorrectCount((c) => c + 1);
    recordAttempt(activeChild.token, activeChild.id, {
      subject: "english",
      topic: ENGLISH_TOPIC,
      track: ENGLISH_TRACK,
      question_id: question.id,
      selected_answer: option,
      is_correct: isCorrect,
    }).catch(() => {
      // Progress syncing is best-effort — don't interrupt reading over it.
    });
  }

  function handleNext() {
    setSelected(null);
    setIndex((i) => i + 1);
  }

  const handleRetry = useCallback(() => {
    setIndex(0);
    setSelected(null);
    setCorrectCount(0);
    setShowSummary(false);
  }, []);

  const question = passage?.questions?.[index];
  const isLastQuestion = passage ? index === passage.questions.length - 1 : false;
  const totalQuestions = passage?.questions?.length ?? 0;
  const accuracy = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;
  const summaryStars = starsForAccuracy(accuracy);

  return (
    <div className="app-frame app-frame-wide">
      <ScreenBackground />
      <TopBar
        title={passage?.title ?? "Reading Comprehension"}
        onBack={() => navigate("/english/passages")}
      />
      <div className="screen">
        {loading && <div className="loading-spinner" />}
        {error && <div className="error-banner">{error}</div>}

        {!loading && passage && (
          <>
            <div className="passage-nav">
              <button
                type="button"
                className="btn btn-outline"
                disabled={!prevPassage}
                onClick={() => prevPassage && navigate(`/english/passages/${prevPassage.id}`)}
              >
                ⬅ Previous
              </button>
              <button
                type="button"
                className="btn btn-outline"
                disabled={!nextPassage}
                onClick={() => nextPassage && navigate(`/english/passages/${nextPassage.id}`)}
              >
                Next ➡
              </button>
            </div>

            {showSummary ? (
              <div className="summary-card">
                <div className="mascot">🎉</div>
                <h1 className="title">Passage Complete!</h1>
                <div className="summary-score">
                  {correctCount} / {totalQuestions}
                </div>
                <div className="summary-accuracy">{accuracy}% accuracy</div>
                <Stars count={summaryStars} />
                <div className="summary-message">{encouragementForAccuracy(accuracy)}</div>

                <button type="button" className="btn btn-outline btn-block" onClick={handleRetry}>
                  🔁 Retry This Passage
                </button>

                {nextPassage ? (
                  <button
                    type="button"
                    className="btn btn-accent btn-block"
                    onClick={() => navigate(`/english/passages/${nextPassage.id}`)}
                  >
                    Next Passage ➡️
                  </button>
                ) : (
                  <button
                    type="button"
                    className="btn btn-primary btn-block"
                    onClick={() => navigate("/english/passages")}
                  >
                    🌟 Back to Passages
                  </button>
                )}
              </div>
            ) : (
              <>
                <div className="passage-reading-box">
                  <p>{passage.body}</p>
                </div>

                {question ? (
                  <>
                    <p className="subtitle">
                      Question {index + 1} of {passage.questions.length}
                    </p>

                    <div className="question-card">
                      <div className="question-text">{question.question_text}</div>
                    </div>

                    <div className="option-grid">
                      {question.options.map((option) => {
                        let cls = "option-btn";
                        if (selected !== null) {
                          if (option === question.correct_answer) cls += " correct";
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
                      <div
                        className={`feedback-banner ${
                          selected === question.correct_answer ? "correct" : "wrong"
                        }`}
                      >
                        {selected === question.correct_answer
                          ? "🎉 Correct! Great job!"
                          : "Not quite — you can do it!"}
                      </div>
                    )}

                    {selected !== null && selected !== question.correct_answer && (
                      <div className="solution-panel">
                        <span>💡 {question.explanation_hint}</span>
                        <span>You'll get the next one — keep going!</span>
                      </div>
                    )}

                    {selected !== null && !isLastQuestion && (
                      <button
                        type="button"
                        className="btn btn-primary btn-block"
                        onClick={handleNext}
                      >
                        Next Question ➡️
                      </button>
                    )}

                    {selected !== null && isLastQuestion && (
                      <button
                        type="button"
                        className="btn btn-accent btn-block"
                        onClick={() => setShowSummary(true)}
                      >
                        See My Results ✅
                      </button>
                    )}
                  </>
                ) : (
                  <p className="subtitle">This passage has no questions yet.</p>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
