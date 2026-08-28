import { useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import Mascot from "../components/Mascot";
import ScreenBackground from "../components/ScreenBackground";
import { useAuth } from "../context/AuthContext";
import { apiErrorMessage } from "../api";

const KEYPAD_ROWS = [
  ["1", "2", "3"],
  ["4", "5", "6"],
  ["7", "8", "9"],
  ["back", "0", "ok"],
];

function ChildList({ kids, loading, onPick, isParentLoggedIn, onAddChild, onParentLogin }) {
  return (
    <div className="screen screen-top-centered">
      <Mascot state="encouraging" size="lg" />
      <h1 className="title">Who's Practicing?</h1>

      {loading && kids.length === 0 && (
        <>
          <div className="loading-spinner" />
          <p className="subtitle">Loading children…</p>
        </>
      )}

      {!loading && kids.length === 0 && (
        <p className="subtitle">No children added yet.</p>
      )}

      <div className="child-grid">
        {kids.map((child) => (
          <button
            key={child.id}
            type="button"
            className="child-tile"
            onClick={() => onPick(child)}
          >
            <span className="child-avatar">{child.name.charAt(0).toUpperCase()}</span>
            {child.name}
          </button>
        ))}

        {isParentLoggedIn && (
          <button type="button" className="tile tile-add-child" onClick={onAddChild}>
            <span className="tile-emoji">➕</span>
            Add Child
          </button>
        )}
      </div>

      {!isParentLoggedIn && (
        <button type="button" className="link-btn" onClick={onParentLogin}>
          Parent Login / Sign Up
        </button>
      )}
    </div>
  );
}

function PinPad({ child, onBack, onSuccess }) {
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { loginChildWithPin } = useAuth();

  async function submit(nextPin) {
    setBusy(true);
    setError("");
    try {
      await loginChildWithPin(child.id, nextPin);
      onSuccess();
    } catch (err) {
      setError(apiErrorMessage(err, "Oops! Wrong PIN, try again."));
      setPin("");
    } finally {
      setBusy(false);
    }
  }

  function handleKey(key) {
    if (busy) return;
    if (key === "back") {
      setPin((p) => p.slice(0, -1));
      return;
    }
    if (key === "ok") {
      if (pin.length >= 4) submit(pin);
      return;
    }
    setPin((p) => (p.length < 6 ? p + key : p));
  }

  return (
    <>
      <TopBar title={child.name} onBack={onBack} />
      <div className="screen screen-top-centered">
        <Mascot state="encouraging" />
        <p className="subtitle">Enter your secret PIN</p>

        <div className="pin-dots">
          {Array.from({ length: 6 }, (_, i) => (
            <span key={i} className={`pin-dot ${i < pin.length ? "filled" : ""}`} />
          ))}
        </div>

        {error && <div className="error-banner">{error}</div>}

        <div className="keypad">
          {KEYPAD_ROWS.flat().map((key, i) => (
            <button
              key={i}
              type="button"
              className="key-btn"
              disabled={busy}
              onClick={() => handleKey(key)}
            >
              {key === "back" ? "⌫" : key === "ok" ? "OK" : key}
            </button>
          ))}
        </div>
      </div>
    </>
  );
}

export default function ChildLoginPage() {
  const { cachedChildren, childrenLoading, isParentLoggedIn } = useAuth();
  const [selectedChild, setSelectedChild] = useState(null);
  const navigate = useNavigate();

  if (selectedChild) {
    return (
      <div className="app-frame">
        <ScreenBackground />
        <PinPad
          child={selectedChild}
          onBack={() => setSelectedChild(null)}
          onSuccess={() => navigate("/topics")}
        />
      </div>
    );
  }

  return (
    <div className="app-frame">
      <ScreenBackground />
      <ChildList
        kids={cachedChildren}
        loading={childrenLoading}
        onPick={setSelectedChild}
        isParentLoggedIn={isParentLoggedIn}
        onAddChild={() => navigate("/children/add")}
        onParentLogin={() => navigate("/parent/auth")}
      />
    </div>
  );
}
