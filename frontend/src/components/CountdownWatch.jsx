import { useEffect, useRef, useState } from "react";

const RADIUS = 52;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

function formatTime(totalSeconds) {
  const m = Math.floor(totalSeconds / 60);
  const s = totalSeconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

// A whole-session countdown: mounted once per timed level/passage and left
// running across "Practice More" / prev-next navigation within it (parent
// keeps totalSeconds stable across those), rather than resetting per question.
export default function CountdownWatch({ totalSeconds, onExpire }) {
  const [remaining, setRemaining] = useState(totalSeconds);
  const expiredRef = useRef(false);

  useEffect(() => {
    setRemaining(totalSeconds);
    expiredRef.current = false;
  }, [totalSeconds]);

  useEffect(() => {
    if (remaining <= 0) {
      if (!expiredRef.current) {
        expiredRef.current = true;
        onExpire?.();
      }
      return undefined;
    }
    const id = setTimeout(() => setRemaining((r) => r - 1), 1000);
    return () => clearTimeout(id);
  }, [remaining, onExpire]);

  const fraction = totalSeconds > 0 ? remaining / totalSeconds : 0;
  const dashOffset = CIRCUMFERENCE * (1 - fraction);
  const isDanger = remaining <= Math.min(10, Math.ceil(totalSeconds * 0.15));
  const isWarning = !isDanger && remaining <= Math.ceil(totalSeconds * 0.3);

  let tone = "timer-watch-calm";
  if (isDanger) tone = "timer-watch-danger";
  else if (isWarning) tone = "timer-watch-warning";

  return (
    <div className={`timer-watch ${tone} ${isDanger ? "timer-watch-pulse" : ""}`}>
      <svg viewBox="0 0 120 120" className="timer-watch-svg">
        <circle className="timer-watch-track" cx="60" cy="60" r={RADIUS} />
        <circle
          className="timer-watch-progress"
          cx="60"
          cy="60"
          r={RADIUS}
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={dashOffset}
          transform="rotate(-90 60 60)"
        />
      </svg>
      <div className="timer-watch-face">
        <span className="timer-watch-time">{formatTime(remaining)}</span>
        <span className="timer-watch-label">{remaining > 0 ? "left" : "Time's up!"}</span>
      </div>
    </div>
  );
}
