export default function Stars({ count, max = 3 }) {
  return (
    <div className="stars-row" aria-label={`${count} out of ${max} stars`}>
      {Array.from({ length: max }, (_, i) => (
        <span key={i}>{i < count ? "⭐" : "☆"}</span>
      ))}
    </div>
  );
}
