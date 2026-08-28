import { useMemo, useState } from "react";
import { BACKGROUND_IMAGES } from "../backgroundManifest";

const PLACEMENTS = ["left-tilt", "right-tilt", "full-low-opacity"];

function pickBackground() {
  if (BACKGROUND_IMAGES.length === 0) return null;

  const image = BACKGROUND_IMAGES[Math.floor(Math.random() * BACKGROUND_IMAGES.length)];
  const placement = PLACEMENTS[Math.floor(Math.random() * PLACEMENTS.length)];
  const tilt =
    placement === "left-tilt"
      ? -(8 + Math.random() * 7)
      : placement === "right-tilt"
      ? 8 + Math.random() * 7
      : 0;
  const opacity = placement === "full-low-opacity" ? 0.35 + Math.random() * 0.1 : 0.92;

  return { image, placement, tilt, opacity };
}

// Kid-friendly-ui skill, section 6: one random image + placement per fresh screen
// mount. useMemo runs once per mount (not on re-renders/state changes within the
// same screen) so re-randomization only happens on fresh navigation.
export default function ScreenBackground() {
  const bg = useMemo(pickBackground, []);
  const [loaded, setLoaded] = useState(false);

  if (!bg) return null;

  const { image, placement, tilt, opacity } = bg;
  const wrapperStyle = placement === "full-low-opacity" ? undefined : { transform: `rotate(${tilt.toFixed(1)}deg)` };

  return (
    <div className={`screen-bg screen-bg-${placement}`} aria-hidden="true" style={wrapperStyle}>
      <img
        src={`/backgrounds/${image}`}
        alt=""
        loading="lazy"
        className="screen-bg-img"
        style={{ opacity: loaded ? opacity : 0 }}
        onLoad={() => setLoaded(true)}
      />
      {placement === "full-low-opacity" && <div className="screen-bg-overlay" />}
    </div>
  );
}
