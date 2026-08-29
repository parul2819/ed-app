import { useMemo, useState } from "react";
import { BACKGROUND_IMAGES } from "../backgroundManifest";

const CORNERS = ["top-left", "top-right", "bottom-left", "bottom-right"];

function pickBackground() {
  if (BACKGROUND_IMAGES.length === 0) return null;

  // same image everywhere on a screen: one full low-opacity backdrop plus a
  // small vivid corner accent, so the two reinforce each other instead of
  // competing for attention.
  const image = BACKGROUND_IMAGES[Math.floor(Math.random() * BACKGROUND_IMAGES.length)];
  const fullOpacity = 0.35 + Math.random() * 0.1;

  const corner = CORNERS[Math.floor(Math.random() * CORNERS.length)];
  const tilt = corner.endsWith("left") ? -(8 + Math.random() * 7) : 8 + Math.random() * 7;
  // random small-to-medium size per mount (see index.css .screen-bg-corner)
  const sizeFactor = Math.random();

  return { image, fullOpacity, corner, tilt, sizeFactor };
}

// Kid-friendly-ui skill, section 6: one random image + placement per fresh screen
// mount. useMemo runs once per mount (not on re-renders/state changes within the
// same screen) so re-randomization only happens on fresh navigation.
export default function ScreenBackground() {
  const bg = useMemo(pickBackground, []);
  const [loaded, setLoaded] = useState(false);

  if (!bg) return null;

  const { image, fullOpacity, corner, tilt, sizeFactor } = bg;
  const src = `/backgrounds/${image}`;

  return (
    <>
      <div className="screen-bg screen-bg-full-low-opacity" aria-hidden="true">
        <img
          src={src}
          alt=""
          loading="lazy"
          className="screen-bg-img"
          style={{ opacity: loaded ? fullOpacity : 0 }}
          onLoad={() => setLoaded(true)}
        />
        <div className="screen-bg-overlay" />
      </div>
      <div
        className={`screen-bg screen-bg-corner screen-bg-${corner}`}
        aria-hidden="true"
        style={{ transform: `rotate(${tilt.toFixed(1)}deg)`, "--bg-size-factor": sizeFactor.toFixed(3) }}
      >
        <img
          src={src}
          alt=""
          loading="lazy"
          className="screen-bg-img"
          style={{ opacity: loaded ? 0.92 : 0 }}
        />
      </div>
    </>
  );
}
