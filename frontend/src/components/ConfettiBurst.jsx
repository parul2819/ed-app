const PIECES = [
  { angle: -70, color: "var(--pastel-pink-dark)" },
  { angle: -40, color: "var(--pastel-yellow-dark)" },
  { angle: -15, color: "var(--pastel-mint-dark)" },
  { angle: 15, color: "var(--pastel-blue-dark)" },
  { angle: 40, color: "var(--pastel-lavender-dark)" },
  { angle: 70, color: "var(--color-accent-2)" },
];

export default function ConfettiBurst() {
  return (
    <div className="confetti-burst" aria-hidden="true">
      {PIECES.map((piece, i) => (
        <span
          key={i}
          className="confetti-piece"
          style={{
            "--angle": `${piece.angle}deg`,
            "--delay": `${i * 30}ms`,
            background: piece.color,
          }}
        />
      ))}
    </div>
  );
}
