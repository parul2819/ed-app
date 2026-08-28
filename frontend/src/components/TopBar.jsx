function BackIcon() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
      <path
        d="M15 5 L8 12 L15 19"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function TopBar({ title, onBack, actions = [] }) {
  return (
    <div className="topbar">
      {onBack ? (
        <button type="button" className="topbar-btn topbar-back" onClick={onBack}>
          <BackIcon />
          Back
        </button>
      ) : (
        <span style={{ width: 64 }} />
      )}
      <h1>{title}</h1>
      {actions.length > 0 ? (
        <div className="topbar-actions">
          {actions.map((action) => (
            <button
              key={action.label}
              type="button"
              className={`topbar-btn${actions.length > 1 ? " topbar-btn-sm" : ""}`}
              onClick={action.onClick}
            >
              {action.label}
            </button>
          ))}
        </div>
      ) : (
        <span style={{ width: 64 }} />
      )}
    </div>
  );
}
