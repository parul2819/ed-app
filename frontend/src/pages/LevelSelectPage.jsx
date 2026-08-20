import { useNavigate, useParams } from "react-router-dom";
import TopBar from "../components/TopBar";
import { useAuth } from "../context/AuthContext";
import { LEVELS_BY_TRACK, TOPIC_LABELS } from "../constants";

function capitalize(word) {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

export default function LevelSelectPage() {
  const { track, topic } = useParams();
  const navigate = useNavigate();
  const { activeChild, logoutChild, signOut } = useAuth();
  const levels = LEVELS_BY_TRACK[track] ?? [];

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
      <TopBar
        title={title}
        onBack={() => navigate("/topics")}
        actions={[
          { label: "Switch", onClick: handleSwitchChild },
          { label: "Sign out", onClick: handleSignOut },
        ]}
      />
      <div className="screen">
        <p className="subtitle">Hi {activeChild?.name ?? "there"}, pick your level!</p>
        <div className="level-list">
          {levels.map((level) => (
            <button
              key={level.key}
              type="button"
              className={`level-card level-${level.key}`}
              onClick={() => navigate(`/practice/${track}/${topic}/${level.key}`)}
            >
              <span className="level-emoji">{level.emoji}</span>
              <span className="level-info">
                <span className="level-title">{level.label}</span>
                <span className="level-desc">{level.desc}</span>
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
