import { useState } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../components/TopBar";
import Mascot from "../components/Mascot";
import { useAuth } from "../context/AuthContext";
import { apiErrorMessage } from "../api";

export default function AddChildPage() {
  const [name, setName] = useState("");
  const [pin, setPin] = useState("");
  const [confirmPin, setConfirmPin] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { addChild } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!/^\d{4,6}$/.test(pin)) {
      setError("PIN must be 4 to 6 numbers.");
      return;
    }
    if (pin !== confirmPin) {
      setError("PINs don't match. Try again.");
      return;
    }

    setBusy(true);
    try {
      await addChild(name.trim(), pin, 3);
      navigate("/children");
    } catch (err) {
      setError(apiErrorMessage(err, "Could not add child. Please try again."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-frame">
      <TopBar title="Add a Child" onBack={() => navigate(-1)} />
      <div className="screen">
        <Mascot state="encouraging" />
        <p className="subtitle">Give your child a name and a secret PIN to log in with.</p>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="field">
            <label htmlFor="name">Child's name</label>
            <input
              id="name"
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Meera"
            />
          </div>
          <div className="field">
            <label htmlFor="pin">Secret PIN (4-6 digits)</label>
            <input
              id="pin"
              type="password"
              inputMode="numeric"
              pattern="\d*"
              required
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, "").slice(0, 6))}
            />
          </div>
          <div className="field">
            <label htmlFor="confirmPin">Type the PIN again</label>
            <input
              id="confirmPin"
              type="password"
              inputMode="numeric"
              pattern="\d*"
              required
              value={confirmPin}
              onChange={(e) => setConfirmPin(e.target.value.replace(/\D/g, "").slice(0, 6))}
            />
          </div>

          {error && <div className="error-banner">{error}</div>}

          <button type="submit" className="btn btn-primary btn-block" disabled={busy}>
            {busy ? "Adding…" : "Add Child"}
          </button>
        </form>
      </div>
    </div>
  );
}
