export const TOPIC_LABELS = {
  addition: "Addition",
  subtraction: "Subtraction",
  multiplication: "Multiplication",
};

export const LEVELS_BY_TRACK = {
  school: [
    { key: "easy", label: "Easy", emoji: "🌱", desc: "Start simple and build confidence" },
    { key: "medium", label: "Medium", emoji: "🌤️", desc: "A bit more of a challenge" },
    { key: "hard", label: "Hard", emoji: "🔥", desc: "Push yourself further" },
  ],
  olympiad: [
    { key: "super_hard", label: "Super Hard", emoji: "🚀", desc: "Olympiad-style multi-step problems" },
    { key: "pro", label: "Pro", emoji: "🏆", desc: "The toughest puzzles and patterns" },
  ],
};

export function levelLabel(track, difficulty) {
  const level = LEVELS_BY_TRACK[track]?.find((l) => l.key === difficulty);
  return level?.label ?? difficulty;
}
