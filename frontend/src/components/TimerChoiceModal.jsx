const TIMER_OPTIONS = [
  { seconds: null, label: "No Timer", emoji: "🐢", desc: "Take your time" },
  { seconds: 180, label: "3 min", emoji: "⏱️", desc: "Quick sprint" },
  { seconds: 300, label: "5 min", emoji: "⏰", desc: "Steady pace" },
  { seconds: 600, label: "10 min", emoji: "⏳", desc: "Relaxed round" },
];

export default function TimerChoiceModal({ open, onChoose, onCancel }) {
  if (!open) return null;

  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-emoji">⏱️</div>
        <h2 className="modal-title">Race the clock?</h2>
        <p className="modal-subtitle">Pick how you'd like to practice this one.</p>
        <div className="timer-choice-grid">
          {TIMER_OPTIONS.map((opt) => (
            <button
              key={opt.label}
              type="button"
              className="timer-choice-btn"
              onClick={() => onChoose(opt.seconds)}
            >
              <span className="timer-choice-emoji">{opt.emoji}</span>
              <span className="timer-choice-label">{opt.label}</span>
              <span className="timer-choice-desc">{opt.desc}</span>
            </button>
          ))}
        </div>
        <button type="button" className="link-btn" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  );
}
