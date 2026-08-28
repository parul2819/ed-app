import { useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import Mascot from "../components/Mascot";
import ScreenBackground from "../components/ScreenBackground";
import { useAuth } from "../context/AuthContext";

const TOPICS = [
  { key: "addition", label: "Addition", emoji: "➕", className: "tile-addition" },
  { key: "subtraction", label: "Subtraction", emoji: "➖", className: "tile-subtraction" },
  { key: "multiplication", label: "Multiply", emoji: "✖️", className: "tile-multiplication" },
];

export default function TopicSelectPage() {
  const [track, setTrack] = useState("school");
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
          {TOPICS.map((topic) => (
            <button
              key={topic.key}
              type="button"
              className={`tile ${topic.className}`}
              onClick={() => navigate(`/levels/${track}/${topic.key}`)}
            >
              <span className="tile-emoji">{topic.emoji}</span>
              {topic.label}
            </button>
          ))}
        </div>

        <button type="button" className="btn btn-outline btn-block" onClick={() => navigate("/progress")}>
          ⭐ My Progress
        </button>
      </div>
    </div>
  );
}
