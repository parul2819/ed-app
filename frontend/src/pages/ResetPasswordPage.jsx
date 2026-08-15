import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import TopBar from "../components/TopBar";
import { resetPassword, apiErrorMessage } from "../api";

export default function ResetPasswordPage() {
  const { token: tokenFromUrl } = useParams();
  const [token, setToken] = useState(tokenFromUrl || "");
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await resetPassword(token, newPassword);
      navigate("/parent/auth");
    } catch (err) {
      setError(apiErrorMessage(err, "Could not reset password. Please try again."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-frame">
      <TopBar title="Reset Password" onBack={() => navigate(-1)} />
      <div className="screen screen-centered">
        <div className="mascot">🔑</div>
        <p className="subtitle">
          Enter the reset token from the backend console/logs and choose a new
          password.
        </p>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="field">
            <label htmlFor="token">Reset token</label>
            <input
              id="token"
              type="text"
              required
              value={token}
              onChange={(e) => setToken(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="newPassword">New password</label>
            <input
              id="newPassword"
              type="password"
              autoComplete="new-password"
              minLength={8}
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
          </div>

          {error && <div className="error-banner">{error}</div>}

          <button type="submit" className="btn btn-primary btn-block" disabled={busy}>
            {busy ? "Please wait…" : "Reset Password"}
          </button>
        </form>
      </div>
    </div>
  );
}
