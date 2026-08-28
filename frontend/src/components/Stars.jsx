function StarIcon({ filled }) {
  return (
    <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true">
      <path
        d="M12 2.5 L14.9 9 L22 9.7 L16.7 14.5 L18.2 21.5 L12 17.9 L5.8 21.5 L7.3 14.5 L2 9.7 L9.1 9 Z"
        fill={filled ? "var(--color-accent-2)" : "none"}
        stroke={filled ? "var(--color-accent-2)" : "var(--color-muted)"}
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function Stars({ count, max = 3 }) {
  return (
    <div className="stars-row" aria-label={`${count} out of ${max} stars`}>
      {Array.from({ length: max }, (_, i) => (
        <StarIcon key={i} filled={i < count} />
      ))}
    </div>
  );
}
