import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import Mascot from "../components/Mascot";
import ScreenBackground from "../components/ScreenBackground";
import { useAuth } from "../context/AuthContext";

const SUBJECTS = [
  { key: "maths", label: "Maths", emoji: "🔢", className: "tile-maths", path: "/maths/topics" },
  {
    key: "english",
    label: "English",
    emoji: "📖",
    className: "tile-english",
    path: "/english/passages",
  },
];

export default function SubjectSelectPage() {
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
        actions={[
          { label: "Switch", onClick: handleSwitchChild },
          { label: "Sign out", onClick: handleSignOut },
        ]}
      />
      <div className="screen screen-top-centered">
        <Mascot state="encouraging" />
        <p className="subtitle">What do you want to practice today?</p>

        <div className="tile-grid">
          {SUBJECTS.map((subject) => (
            <button
              key={subject.key}
              type="button"
              className={`tile ${subject.className}`}
              onClick={() => navigate(subject.path)}
            >
              <span className="tile-emoji">{subject.emoji}</span>
              {subject.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
