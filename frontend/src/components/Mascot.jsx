const FACES = {
  happy: (
    <>
      <circle cx="41" cy="52" r="9" fill="#ffffff" />
      <circle cx="79" cy="52" r="9" fill="#ffffff" />
      <path d="M37 51 q4 -6 8 0" stroke="#3a2e52" strokeWidth="3" fill="none" strokeLinecap="round" />
      <path d="M75 51 q4 -6 8 0" stroke="#3a2e52" strokeWidth="3" fill="none" strokeLinecap="round" />
      <circle cx="30" cy="64" r="6" fill="#ffb9d6" opacity="0.8" />
      <circle cx="90" cy="64" r="6" fill="#ffb9d6" opacity="0.8" />
      <path
        d="M50 66 q10 12 20 0"
        stroke="#3a2e52"
        strokeWidth="3.5"
        fill="none"
        strokeLinecap="round"
      />
    </>
  ),
  confused: (
    <>
      <circle cx="41" cy="53" r="8" fill="#ffffff" />
      <circle cx="79" cy="53" r="8" fill="#ffffff" />
      <circle cx="43" cy="54" r="4" fill="#3a2e52" />
      <circle cx="77" cy="52" r="4" fill="#3a2e52" />
      <path d="M33 43 q8 -6 14 -1" stroke="#3a2e52" strokeWidth="3" fill="none" strokeLinecap="round" />
      <path d="M73 42 q8 -3 14 4" stroke="#3a2e52" strokeWidth="3" fill="none" strokeLinecap="round" />
      <path
        d="M52 68 q4 -5 8 0 q4 5 8 0"
        stroke="#3a2e52"
        strokeWidth="3.5"
        fill="none"
        strokeLinecap="round"
      />
    </>
  ),
  encouraging: (
    <>
      <circle cx="41" cy="52" r="9" fill="#ffffff" />
      <circle cx="79" cy="52" r="9" fill="#ffffff" />
      <circle cx="41" cy="52" r="4.5" fill="#3a2e52" />
      <circle cx="79" cy="52" r="4.5" fill="#3a2e52" />
      <path
        d="M53 68 q7 6 14 0"
        stroke="#3a2e52"
        strokeWidth="3.5"
        fill="none"
        strokeLinecap="round"
      />
    </>
  ),
};

const SIZE_MAP = { sm: 56, md: 88, lg: 128 };

export default function Mascot({ state = "encouraging", size = "md", className = "" }) {
  const px = typeof size === "number" ? size : SIZE_MAP[size] ?? SIZE_MAP.md;
  const face = FACES[state] ?? FACES.encouraging;

  return (
    <div
      className={`mascot-wrap mascot-${state} ${className}`.trim()}
      style={{ width: px, height: px }}
      role="img"
      aria-label={
        state === "happy" ? "Happy owl mascot" : state === "confused" ? "Confused owl mascot" : "Encouraging owl mascot"
      }
    >
      <svg viewBox="0 0 120 120" width="100%" height="100%">
        <ellipse cx="60" cy="112" rx="16" ry="4" fill="#3a2e52" opacity="0.12" />

        <path
          d="M60 6 C30 6 16 30 16 58 C16 88 34 108 60 108 C86 108 104 88 104 58 C104 30 90 6 60 6 Z"
          fill="url(#mascotBody)"
        />

        <path d="M20 26 L36 18 L34 40 Z" fill="#c9b6ff" />
        <path d="M100 26 L84 18 L86 40 Z" fill="#c9b6ff" />

        <ellipse cx="60" cy="60" rx="34" ry="30" fill="#fffaf2" />

        <ellipse cx="14" cy="70" rx="10" ry="16" fill="url(#mascotBody)" opacity="0.9" />
        <ellipse cx="106" cy="70" rx="10" ry="16" fill="url(#mascotBody)" opacity="0.9" />

        {face}

        <path d="M55 60 L65 60 L60 70 Z" fill="#ffb457" />

        <ellipse cx="46" cy="106" rx="8" ry="5" fill="#ffb457" />
        <ellipse cx="74" cy="106" rx="8" ry="5" fill="#ffb457" />

        <defs>
          <linearGradient id="mascotBody" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#c9b6ff" />
            <stop offset="100%" stopColor="#9b7bf5" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}
