import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import Stars from "../components/Stars";
import ScreenBackground from "../components/ScreenBackground";
import { useAuth } from "../context/AuthContext";
import { getChildProgress, getPassageProgress, apiErrorMessage } from "../api";

const TOPICS = [
  { key: "addition", label: "Addition", emoji: "➕" },
  { key: "subtraction", label: "Subtraction", emoji: "➖" },
  { key: "multiplication", label: "Multiply", emoji: "✖️" },
];

// Matches the subject/topic/track values PassagePage records attempts under.
const ENGLISH_SUBJECT = "english";
const ENGLISH_TOPIC = "comprehension";
const ENGLISH_TRACK = "school";

function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function ProgressPage() {
  const [track, setTrack] = useState("school");
  const [progress, setProgress] = useState([]);
  const [passageHistory, setPassageHistory] = useState([]);
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
      const [rows, history] = await Promise.all([
        getChildProgress(activeChild.token, activeChild.id),
        getPassageProgress(activeChild.token, activeChild.id),
      ]);
      setProgress(rows);
      setPassageHistory(history);
    } catch (err) {
      setError(apiErrorMessage(err, "Couldn't load progress right now."));
    } finally {
      setLoading(false);
    }
  }, [activeChild]);

  useEffect(() => {
    loadProgress();
  }, [loadProgress]);

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

        {loading && (
          <>
            <div className="loading-spinner" />
            <p className="subtitle">Loading your stars…</p>
          </>
        )}

        {error && <div className="error-banner">{error}</div>}

        {!loading &&
          !error &&
          TOPICS.map((topic) => {
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

        {!loading && !error && (
          <>
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
      </div>
    </div>
  );
}
