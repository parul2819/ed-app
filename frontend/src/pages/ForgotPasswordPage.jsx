import { useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import Mascot from "../components/Mascot";
import ScreenBackground from "../components/ScreenBackground";
import { forgotPassword, apiErrorMessage } from "../api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await forgotPassword(email);
      setSubmitted(true);
    } catch (err) {
      setError(apiErrorMessage(err, "Something went wrong. Please try again."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-frame">
      <ScreenBackground />
      <TopBar title="Forgot Password" onBack={() => navigate(-1)} />
      <div className="screen screen-centered">
        <Mascot state="encouraging" size="lg" />

        {submitted ? (
          <>
            <p className="subtitle">
              If an account with that email exists, a reset token has been sent.
            </p>
            <p className="subtitle">
              During development, check the backend console/logs for the reset
              token, then enter it on the next screen.
            </p>
            <button
              type="button"
              className="btn btn-primary btn-block"
              onClick={() => navigate("/parent/reset-password")}
            >
              I have my reset token
            </button>
          </>
        ) : (
          <>
            <p className="subtitle">
              Enter your email and we'll generate a password reset token.
            </p>
            <form
              onSubmit={handleSubmit}
              style={{ display: "flex", flexDirection: "column", gap: 16 }}
            >
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

              {error && <div className="error-banner">{error}</div>}

              <button type="submit" className="btn btn-primary btn-block" disabled={busy}>
                {busy ? "Please wait…" : "Send Reset Token"}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
