import { useMemo, useState } from "react";
import { BACKGROUND_IMAGES } from "../backgroundManifest";

const CORNERS = ["top-left", "top-right", "bottom-left", "bottom-right"];

function pickBackground() {
  if (BACKGROUND_IMAGES.length === 0) return null;

  const image = BACKGROUND_IMAGES[Math.floor(Math.random() * BACKGROUND_IMAGES.length)];

  // keep full-low-opacity at its original 1-in-3 odds; the remaining 2-in-3
  // now spread evenly across all 4 corners instead of just left/right.
  if (Math.random() < 1 / 3) {
    return {
      image,
      placement: "full-low-opacity",
      tilt: 0,
      opacity: 0.35 + Math.random() * 0.1,
    };
  }

  const placement = CORNERS[Math.floor(Math.random() * CORNERS.length)];
  const tilt = placement.endsWith("left") ? -(8 + Math.random() * 7) : 8 + Math.random() * 7;
  // random small-to-medium size per mount (see index.css .screen-bg-corner)
  const sizeFactor = Math.random();

  return { image, placement, tilt, opacity: 0.92, sizeFactor };
}

// Kid-friendly-ui skill, section 6: one random image + placement per fresh screen
// mount. useMemo runs once per mount (not on re-renders/state changes within the
// same screen) so re-randomization only happens on fresh navigation.
export default function ScreenBackground() {
  const bg = useMemo(pickBackground, []);
  const [loaded, setLoaded] = useState(false);

  if (!bg) return null;

  const { image, placement, tilt, opacity, sizeFactor } = bg;
  const isCorner = placement !== "full-low-opacity";
  const wrapperStyle = isCorner
    ? { transform: `rotate(${tilt.toFixed(1)}deg)`, "--bg-size-factor": sizeFactor.toFixed(3) }
    : undefined;
  const className = isCorner
    ? `screen-bg screen-bg-corner screen-bg-${placement}`
    : "screen-bg screen-bg-full-low-opacity";

  return (
    <div className={className} aria-hidden="true" style={wrapperStyle}>
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
