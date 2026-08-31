import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import TopBar from "../components/TopBar";
import ScreenBackground from "../components/ScreenBackground";
import TimerChoiceModal from "../components/TimerChoiceModal";
import { useAuth } from "../context/AuthContext";
import { LEVELS_BY_TRACK, TOPIC_LABELS } from "../constants";
import { getAttemptHistory } from "../api";

function capitalize(word) {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

// Sums every practice round recorded at each difficulty for this topic/track
// into a running attempted/correct total, so a level card can show how far
// along the child is at that level -- mirrors the cumulative philosophy of
// ProgressPage's "Overview" tab (running totals) rather than best-attempt-only.
function summarizeByDifficulty(history, topic, track) {
  const map = {};
  for (const round of history) {
    if (round.subject !== "maths" || round.topic !== topic || round.track !== track) continue;
    if (!round.difficulty) continue;
    const entry = map[round.difficulty] ?? { attempted: 0, correct: 0 };
    entry.attempted += round.questions_attempted;
    entry.correct += round.questions_correct;
    map[round.difficulty] = entry;
  }
  return map;
}

export default function LevelSelectPage() {
  const { track, topic } = useParams();
  const navigate = useNavigate();
  const { activeChild, logoutChild, signOut } = useAuth();
  const levels = LEVELS_BY_TRACK[track] ?? [];
  const [pendingLevel, setPendingLevel] = useState(null);
  const [progressByDifficulty, setProgressByDifficulty] = useState({});

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const history = await getAttemptHistory(activeChild.token, activeChild.id);
        if (!cancelled) setProgressByDifficulty(summarizeByDifficulty(history, topic, track));
      } catch {
        // Progress bars are a nice-to-have -- level selection still works without them.
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [activeChild, topic, track]);

  function handleChooseTimer(timerSeconds) {
    const level = pendingLevel;
    setPendingLevel(null);
    navigate(`/practice/${track}/${topic}/${level.key}`, { state: { timerSeconds } });
  }

  function handleSwitchChild() {
    logoutChild();
    navigate("/children");
  }

  function handleSignOut() {
    signOut();
    navigate("/parent/auth");
  }

  const title = `${TOPIC_LABELS[topic] ?? capitalize(topic)} · ${capitalize(track)}`;

  return (
    <div className="app-frame">
      <ScreenBackground />
      <TopBar
        title={title}
        onBack={() => navigate("/maths/topics")}
        actions={[
          { label: "Switch", onClick: handleSwitchChild },
          { label: "Sign out", onClick: handleSignOut },
        ]}
      />
      <div className="screen">
        <p className="subtitle">Hi {activeChild?.name ?? "there"}, pick your level!</p>
        <div className="level-list">
          {levels.map((level) => {
            const stats = progressByDifficulty[level.key];
            const attempted = stats?.attempted ?? 0;
            const correct = stats?.correct ?? 0;
            const accuracy = attempted > 0 ? Math.round((correct / attempted) * 100) : 0;
            return (
              <button
                key={level.key}
                type="button"
                className={`level-card level-${level.key}`}
                onClick={() => setPendingLevel(level)}
              >
                <span className="level-emoji">{level.emoji}</span>
                <span className="level-info">
                  <span className="level-title">{level.label}</span>
                  <span className="level-desc">{level.desc}</span>
                  <span className="level-progress">
                    <span className="level-progress-bar">
                      <span
                        className="level-progress-fill"
                        style={{ width: `${accuracy}%` }}
                      />
                    </span>
                    <span className="level-progress-caption">
                      {attempted > 0
                        ? `${correct}/${attempted} correct · ${accuracy}%`
                        : "Not started yet"}
                    </span>
                  </span>
                </span>
              </button>
            );
          })}
        </div>
      </div>
      <TimerChoiceModal
        open={pendingLevel !== null}
        onChoose={handleChooseTimer}
        onCancel={() => setPendingLevel(null)}
      />
    </div>
  );
}
