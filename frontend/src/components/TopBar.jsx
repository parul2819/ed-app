export default function TopBar({ title, onBack, actions = [] }) {
  return (
    <div className="topbar">
      {onBack ? (
        <button type="button" className="topbar-btn" onClick={onBack}>
          ← Back
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
