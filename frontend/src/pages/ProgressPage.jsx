import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import Stars from "../components/Stars";
import ScreenBackground from "../components/ScreenBackground";
import { useAuth } from "../context/AuthContext";
import { getChildProgress, apiErrorMessage } from "../api";

const TOPICS = [
  { key: "addition", label: "Addition", emoji: "➕" },
  { key: "subtraction", label: "Subtraction", emoji: "➖" },
  { key: "multiplication", label: "Multiply", emoji: "✖️" },
];

export default function ProgressPage() {
  const [track, setTrack] = useState("school");
  const [progress, setProgress] = useState([]);
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
      const rows = await getChildProgress(activeChild.token, activeChild.id);
      setProgress(rows);
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
        onBack={() => navigate("/topics")}
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
      </div>
    </div>
  );
}
