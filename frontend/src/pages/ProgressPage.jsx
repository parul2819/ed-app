import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import Stars from "../components/Stars";
import ConfettiBurst from "../components/ConfettiBurst";
import ScreenBackground from "../components/ScreenBackground";
import { useAuth } from "../context/AuthContext";
import {
  getChildProgress,
  getPassageProgress,
  getAttemptHistory,
  apiErrorMessage,
} from "../api";
import { levelLabel } from "../constants";

const TOPICS = [
  { key: "addition", label: "Addition", emoji: "➕" },
  { key: "subtraction", label: "Subtraction", emoji: "➖" },
  { key: "multiplication", label: "Multiply", emoji: "✖️" },
];
const TOPIC_ORDER = TOPICS.map((t) => t.key);
const TRACK_ORDER = ["school", "olympiad"];

// Matches the subject/topic/track values PassagePage records attempts under.
const ENGLISH_SUBJECT = "english";
const ENGLISH_TOPIC = "comprehension";
const ENGLISH_TRACK = "school";

function capitalize(word) {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function percentFor(round) {
  return round.questions_attempted > 0
    ? Math.round((round.questions_correct / round.questions_attempted) * 100)
    : 0;
}

function tierForPercent(percent) {
  if (percent >= 90) return "great";
  if (percent >= 70) return "good";
  return "keep-trying";
}

// Groups the flat, chronological attempt-history feed into one card per
// level/passage the child has ever practiced, each holding its own ordered
// list of attempts (Try 1, Try 2, ...).
function groupAttemptHistory(history) {
  const groups = new Map();
  for (const round of history) {
    const key =
      round.subject === "english"
        ? `english:${round.passage_id}`
        : `maths:${round.topic}:${round.track}:${round.difficulty}`;
    if (!groups.has(key)) groups.set(key, { key, sample: round, attempts: [] });
    groups.get(key).attempts.push(round);
  }

  const mathsGroups = [];
  const englishGroups = [];
  for (const group of groups.values()) {
    if (group.sample.subject === "english") englishGroups.push(group);
    else mathsGroups.push(group);
  }

  mathsGroups.sort((a, b) => {
    const byTopic = TOPIC_ORDER.indexOf(a.sample.topic) - TOPIC_ORDER.indexOf(b.sample.topic);
    if (byTopic !== 0) return byTopic;
    const byTrack = TRACK_ORDER.indexOf(a.sample.track) - TRACK_ORDER.indexOf(b.sample.track);
    if (byTrack !== 0) return byTrack;
    return (a.sample.difficulty ?? "").localeCompare(b.sample.difficulty ?? "");
  });
  englishGroups.sort(
    (a, b) => (a.sample.passage_difficulty_rank ?? 0) - (b.sample.passage_difficulty_rank ?? 0)
  );

  return { mathsGroups, englishGroups };
}

function bestAttemptIndex(attempts) {
  let best = 0;
  for (let i = 1; i < attempts.length; i++) {
    if (percentFor(attempts[i]) > percentFor(attempts[best])) best = i;
  }
  return best;
}

function AttemptChip({ attempt, tryNumber, isBest }) {
  const percent = percentFor(attempt);
  const tier = tierForPercent(percent);
  return (
    <div className={`attempt-chip attempt-chip-${tier}`}>
      {percent === 100 && <ConfettiBurst />}
      {isBest && (
        <span className="attempt-chip-crown" title="Best attempt so far">
          👑
        </span>
      )}
      <span className="attempt-chip-number">Try {tryNumber}</span>
      <span className="attempt-chip-score">
        {attempt.questions_correct}/{attempt.questions_attempted}
      </span>
      <span className="attempt-chip-percent">{percent}%</span>
    </div>
  );
}

function AttemptGroup({ emoji, title, attempts }) {
  const bestIndex = bestAttemptIndex(attempts);
  return (
    <div className="attempt-group">
      <div className="attempt-group-header">
        <span className="attempt-group-emoji">{emoji}</span>
        <span className="attempt-group-title">{title}</span>
        <span className="attempt-group-count">
          {attempts.length} attempt{attempts.length === 1 ? "" : "s"}
        </span>
      </div>
      <div className="attempt-chip-row">
        {attempts.map((attempt, i) => (
          <AttemptChip
            key={attempt.session_id}
            attempt={attempt}
            tryNumber={i + 1}
            isBest={attempts.length > 1 && i === bestIndex}
          />
        ))}
      </div>
    </div>
  );
}

export default function ProgressPage() {
  const [view, setView] = useState("overview");
  const [track, setTrack] = useState("school");
  const [progress, setProgress] = useState([]);
  const [passageHistory, setPassageHistory] = useState([]);
  const [attemptHistory, setAttemptHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { activeChild, logoutChild, signOut } = useAuth();
  const navigate = useNavigate();

  function handleSwitchChild() {
    logoutChild();
    navigate("/children");
  }

  function handleSignOut() {
    signOut();
    navigate("/parent/auth");
  }

  const loadProgress = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [rows, history, attempts] = await Promise.all([
        getChildProgress(activeChild.token, activeChild.id),
        getPassageProgress(activeChild.token, activeChild.id),
        getAttemptHistory(activeChild.token, activeChild.id),
      ]);
      setProgress(rows);
      setPassageHistory(history);
      setAttemptHistory(attempts);
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't load progress right now."));
    } finally {
      setLoading(false);
    }
  }, [activeChild]);

  useEffect(() => {
    loadProgress();
  }, [loadProgress]);

  const { mathsGroups, englishGroups } = groupAttemptHistory(attemptHistory);

  return (
    <div className="app-frame">
      <ScreenBackground />
      <TopBar
        title="My Progress"
        onBack={() => navigate("/subjects")}
        actions={[
          { label: "Switch", onClick: handleSwitchChild },
          { label: "Sign out", onClick: handleSignOut },
        ]}
      />
      <div className="screen">
        <div className="btn-tabs">
          <button
            type="button"
            className={`btn-tab ${view === "overview" ? "active" : ""}`}
            onClick={() => setView("overview")}
          >
            ⭐ Overview
          </button>
          <button
            type="button"
            className={`btn-tab ${view === "attempts" ? "active" : ""}`}
            onClick={() => setView("attempts")}
          >
            🎯 My Attempts
          </button>
        </div>

        {loading && (
          <>
            <div className="loading-spinner" />
            <p className="subtitle">Loading your stars…</p>
          </>
        )}

        {error && <div className="error-banner">{error}</div>}

        {!loading && !error && view === "overview" && (
          <>
            <div className="btn-tabs">
              <button
                type="button"
                className={`btn-tab ${track === "school" ? "active" : ""}`}
                onClick={() => setTrack("school")}
              >
                School
              </button>
              <button
                type="button"
                className={`btn-tab ${track === "olympiad" ? "active" : ""}`}
                onClick={() => setTrack("olympiad")}
              >
                Olympiad
              </button>
            </div>

            {TOPICS.map((topic) => {
              const entry = progress.find(
                (row) => row.topic === topic.key && row.track === track
              );
              const attempted = entry?.questions_attempted ?? 0;
              const correct = entry?.questions_correct ?? 0;
              const accuracy = attempted > 0 ? Math.round((correct / attempted) * 100) : 0;
              const stars = entry?.stars_earned ?? 0;

              return (
                <div className="progress-card" key={topic.key}>
                  <div className="progress-info">
                    <span className="progress-topic">
                      {topic.emoji} {topic.label}
                    </span>
                    <span className="progress-accuracy">
                      {attempted > 0
                        ? `${accuracy}% correct · ${attempted} question${attempted === 1 ? "" : "s"}`
                        : "Not started yet"}
                    </span>
                  </div>
                  <Stars count={stars} />
                </div>
              );
            })}

            <p className="subtitle">📖 English</p>
            {(() => {
              const entry = progress.find(
                (row) =>
                  row.subject === ENGLISH_SUBJECT &&
                  row.topic === ENGLISH_TOPIC &&
                  row.track === ENGLISH_TRACK
              );
              const attempted = entry?.questions_attempted ?? 0;
              const correct = entry?.questions_correct ?? 0;
              const accuracy = attempted > 0 ? Math.round((correct / attempted) * 100) : 0;
              const stars = entry?.stars_earned ?? 0;

              return (
                <div className="progress-card">
                  <div className="progress-info">
                    <span className="progress-topic">📖 Reading Comprehension</span>
                    <span className="progress-accuracy">
                      {attempted > 0
                        ? `${accuracy}% correct · ${attempted} question${attempted === 1 ? "" : "s"}`
                        : "Not started yet"}
                    </span>
                  </div>
                  <Stars count={stars} />
                </div>
              );
            })()}

            {passageHistory.length > 0 && (
              <>
                <p className="subtitle">Passages Read</p>
                {passageHistory.map((row) => {
                  const passageAccuracy =
                    row.questions_attempted > 0
                      ? Math.round((row.questions_correct / row.questions_attempted) * 100)
                      : 0;
                  return (
                    <div className="progress-card" key={row.passage_id}>
                      <div className="progress-info">
                        <span className="progress-topic">
                          {row.title} · Level {row.difficulty_rank}
                        </span>
                        <span className="progress-accuracy">
                          {row.questions_correct}/{row.questions_attempted} correct ·{" "}
                          {passageAccuracy}% accuracy
                        </span>
                        <span className="progress-date">
                          Last read {formatDate(row.last_attempted_at)}
                        </span>
                      </div>
                      <Stars count={row.stars_earned} />
                    </div>
                  );
                })}
              </>
            )}
          </>
        )}

        {!loading && !error && view === "attempts" && (
          <>
            {mathsGroups.length === 0 && englishGroups.length === 0 && (
              <>
                <p className="subtitle">
                  No attempts yet — go answer some questions and come back to see your scores! 🚀
                </p>
              </>
            )}

            {mathsGroups.length > 0 && <p className="subtitle">🧮 Maths</p>}
            {mathsGroups.map((group) => {
              const topicMeta = TOPICS.find((t) => t.key === group.sample.topic);
              const level = group.sample.difficulty
                ? ` · ${levelLabel(group.sample.track, group.sample.difficulty)}`
                : "";
              const title = `${topicMeta?.label ?? capitalize(group.sample.topic)} · ${capitalize(
                group.sample.track
              )}${level}`;
              return (
                <AttemptGroup
                  key={group.key}
                  emoji={topicMeta?.emoji ?? "🧮"}
                  title={title}
                  attempts={group.attempts}
                />
              );
            })}

            {englishGroups.length > 0 && <p className="subtitle">📖 English</p>}
            {englishGroups.map((group) => (
              <AttemptGroup
                key={group.key}
                emoji="📖"
                title={`${group.sample.passage_title} · Level ${group.sample.passage_difficulty_rank}`}
                attempts={group.attempts}
              />
            ))}
          </>
        )}
      </div>
    </div>
  );
}
