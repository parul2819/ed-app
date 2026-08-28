import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiErrorMessage } from "../api";
import Mascot from "../components/Mascot";
import ScreenBackground from "../components/ScreenBackground";

export default function ParentAuthPage() {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { signupParent, loginParent } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "signup") {
        await signupParent(email, password);
      } else {
        await loginParent(email, password);
      }
      navigate("/children");
    } catch (err) {
      setError(apiErrorMessage(err, "Something went wrong. Please try again."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-frame">
      <ScreenBackground />
      <div className="screen screen-centered">
        <Mascot state="encouraging" size="lg" />
        <h1 className="title">Learn with Masti</h1>
        <p className="subtitle">A parent account keeps your child's practice safe.</p>

        <div className="btn-tabs">
          <button
            type="button"
            className={`btn-tab ${mode === "login" ? "active" : ""}`}
            onClick={() => setMode("login")}
          >
            Log In
          </button>
          <button
            type="button"
            className={`btn-tab ${mode === "signup" ? "active" : ""}`}
            onClick={() => setMode("signup")}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="field">
            <label htmlFor="email">Parent email</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              autoComplete={mode === "signup" ? "new-password" : "current-password"}
              minLength={8}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && <div className="error-banner">{error}</div>}

          <button type="submit" className="btn btn-primary btn-block" disabled={busy}>
            {busy ? "Please wait…" : mode === "signup" ? "Create Account" : "Log In"}
          </button>
        </form>

        {mode === "login" && (
          <button
            type="button"
            className="link-btn"
            onClick={() => navigate("/parent/forgot-password")}
          >
            Forgot password?
          </button>
        )}
      </div>
    </div>
  );
}
