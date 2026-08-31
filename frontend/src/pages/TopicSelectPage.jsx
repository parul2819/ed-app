import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import Mascot from "../components/Mascot";
import ScreenBackground from "../components/ScreenBackground";
import { useAuth } from "../context/AuthContext";
import { getChildProgress } from "../api";

const TOPICS = [
  { key: "addition", label: "Addition", emoji: "➕", className: "tile-addition" },
  { key: "subtraction", label: "Subtraction", emoji: "➖", className: "tile-subtraction" },
  { key: "multiplication", label: "Multiply", emoji: "✖️", className: "tile-multiplication" },
  { key: "division", label: "Divide", emoji: "➗", className: "tile-division" },
];

export default function TopicSelectPage() {
  const [track, setTrack] = useState("school");
  const [progress, setProgress] = useState([]);
  const { activeChild, logoutChild, signOut } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const rows = await getChildProgress(activeChild.token, activeChild.id);
        if (!cancelled) setProgress(rows);
      } catch {
        // Progress bars are a nice-to-have -- topic selection still works without them.
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [activeChild]);

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
        title={`Hi, ${activeChild?.name ?? "there"}!`}
        onBack={() => navigate("/subjects")}
        actions={[
          { label: "Switch", onClick: handleSwitchChild },
          { label: "Sign out", onClick: handleSignOut },
        ]}
      />
      <div className="screen screen-top-centered">
        <Mascot state="encouraging" />
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

        <p className="subtitle">Pick something to practice!</p>

        <div className="tile-grid">
          {TOPICS.map((topic) => {
            const entry = progress.find(
              (row) => row.topic === topic.key && row.track === track
            );
            const attempted = entry?.questions_attempted ?? 0;
            const correct = entry?.questions_correct ?? 0;
            const accuracy = attempted > 0 ? Math.round((correct / attempted) * 100) : 0;
            return (
              <button
                key={topic.key}
                type="button"
                className={`tile ${topic.className}`}
                onClick={() => navigate(`/levels/${track}/${topic.key}`)}
              >
                <span className="tile-emoji">{topic.emoji}</span>
                {topic.label}
                {attempted > 0 && (
                  <span className="topic-progress-bar">
                    <span className="topic-progress-fill" style={{ width: `${accuracy}%` }} />
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <button type="button" className="btn btn-outline btn-block" onClick={() => navigate("/progress")}>
          ⭐ My Progress
        </button>
      </div>
    </div>
  );
}
