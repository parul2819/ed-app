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

const BODY_PATH =
  "M60 6 C30 6 16 30 16 58 C16 88 34 108 60 108 C86 108 104 88 104 58 C104 30 90 6 60 6 Z";

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
        {/* soft ground shadow for lift/depth */}
        <ellipse cx="60" cy="113" rx="18" ry="4.5" fill="#3a2e52" opacity="0.16" />

        {/* body: base gradient + rim-shading overlay for a rounded "clay" look */}
        <path d={BODY_PATH} fill="url(#mascotBody)" />
        <path d={BODY_PATH} fill="url(#mascotBodyShade)" />

        {/* glossy shine on the crown, above the belly */}
        <ellipse cx="40" cy="23" rx="17" ry="10" fill="url(#mascotShine)" transform="rotate(-16 40 23)" />

        {/* ear tufts with their own light-to-dark gradient */}
        <path d="M20 26 L36 18 L34 40 Z" fill="url(#mascotEar)" />
        <path d="M100 26 L84 18 L86 40 Z" fill="url(#mascotEar)" />

        {/* belly */}
        <ellipse cx="60" cy="60" rx="34" ry="30" fill="url(#mascotBelly)" />
        <ellipse cx="47" cy="45" rx="10" ry="7" fill="url(#mascotShine)" opacity="0.6" />
        <path d="M32 80 Q60 94 88 80 Q60 88 32 80 Z" fill="#3a2e52" opacity="0.05" />

        {/* side wings with their own gradient + tiny shine */}
        <ellipse cx="14" cy="70" rx="10" ry="16" fill="url(#mascotWing)" />
        <ellipse cx="106" cy="70" rx="10" ry="16" fill="url(#mascotWing)" />
        <ellipse cx="11" cy="64" rx="3.2" ry="6" fill="#ffffff" opacity="0.35" transform="rotate(-18 11 64)" />
        <ellipse cx="109" cy="64" rx="3.2" ry="6" fill="#ffffff" opacity="0.3" transform="rotate(18 109 64)" />

        {face}

        {/* beak */}
        <path d="M55 60 L65 60 L60 70 Z" fill="url(#mascotBeak)" />

        {/* feet with gradient + tiny top-light */}
        <ellipse cx="46" cy="106" rx="8" ry="5" fill="url(#mascotFoot)" />
        <ellipse cx="74" cy="106" rx="8" ry="5" fill="url(#mascotFoot)" />
        <ellipse cx="43.5" cy="104" rx="2.4" ry="1.3" fill="#ffffff" opacity="0.45" />
        <ellipse cx="71.5" cy="104" rx="2.4" ry="1.3" fill="#ffffff" opacity="0.45" />

        <defs>
          <linearGradient id="mascotBody" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ddd0ff" />
            <stop offset="45%" stopColor="#b298f8" />
            <stop offset="100%" stopColor="#8a63e8" />
          </linearGradient>

          <linearGradient id="mascotBodyShade" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.25" />
            <stop offset="55%" stopColor="#ffffff" stopOpacity="0" />
            <stop offset="100%" stopColor="#3a2e52" stopOpacity="0.18" />
          </linearGradient>

          <radialGradient id="mascotShine" cx="35%" cy="30%" r="70%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
          </radialGradient>

          <linearGradient id="mascotEar" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#e4d8ff" />
            <stop offset="100%" stopColor="#a98cf0" />
          </linearGradient>

          <radialGradient id="mascotBelly" cx="38%" cy="28%" r="75%">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="65%" stopColor="#fffaf2" />
            <stop offset="100%" stopColor="#f2e6d2" />
          </radialGradient>

          <linearGradient id="mascotWing" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#d1bfff" />
            <stop offset="100%" stopColor="#8f6eed" />
          </linearGradient>

          <linearGradient id="mascotBeak" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ffcd85" />
            <stop offset="100%" stopColor="#ffa93f" />
          </linearGradient>

          <linearGradient id="mascotFoot" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ffcd85" />
            <stop offset="100%" stopColor="#ffa03a" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}
