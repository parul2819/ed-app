---
name: kid-friendly-ui
description: Visual design system for Learn with Masti's Class 3 child-facing screens — pastel color tokens, mascot owl spec, clay-style buttons/icons, layout/spacing rules, feedback animations, and random background-image placement. Use whenever building, changing, or reviewing any child-facing screen's UI in this app, so new screens stay visually consistent with existing ones without re-specifying the whole system each time.
---

# Kid-Friendly UI — Learn with Masti Design System

Applies to all child-facing screens: parent/child auth, subject selection, Maths
track/topic/level selection, Maths practice, English passage list + reading, completion
screen, progress/dashboard. Does NOT apply to backend logic, API contracts, validation, or
scoring — this skill is frontend/CSS/component only.

## 1. Design tokens

Define once in a central theme file (CSS variables or theme.js), reuse everywhere — never
hardcode raw hex/px values in components.

- **Palette:** pastel-first — soft pink, sky blue, mint, lavender, buttery yellow. 2 slightly
  more saturated accent colors reserved ONLY for primary CTAs and success states. No neon,
  no harsh/bright saturated colors.
- **Fonts:** rounded playful font for headings (Baloo 2 or Fredoka, via Google Fonts), clean
  highly-readable font for body/answer text (these are early readers — legibility over style
  for body copy).
- **Spacing scale:** 4 / 8 / 12 / 16 / 24 / 32 / 48 px. All margins/paddings snap to this scale.
- **Radius scale:** cards min 16px, primary buttons pill-shaped (full radius).
- **Base screen background:** `.app-frame` (and therefore every `.screen`) never sits on a flat
  solid color. Give it a soft pastel gradient built from the palette tokens above, plus a few
  large, soft-edged, low-opacity blob shapes (pure CSS — layered `radial-gradient()`s with a
  transparent fade work well and need no image asset or DOM element) OR a light repeating
  SVG dot/star pattern. This is the base decorative layer everything else in this skill renders
  on top of — in particular, the photo layer in section 6 sits ON TOP OF this base layer, not
  instead of it, so don't let a future screen fall back to a flat `--color-bg` fill. Keep blobs
  low-opacity/pastel-light so body text placed directly on the background (not inside a white/
  pastel card) still meets contrast — cards, tiles, and inputs already have their own solid
  background and are unaffected.

## 2. Mascot — inline SVG owl, no image assets

Single reusable `<Mascot />` component, pure SVG, pastel colors, rounded friendly shapes.
Feel: happy, colorful, lively, appealing — not flat or static. Big expressive eyes, a subtle
looping idle bounce/wiggle animation (CSS keyframes, a few seconds per cycle, not distracting).

Three expression states — build all three as one component with a `state` prop:
- `happy` → correct answer feedback, completion screen
- `confused` → wrong answer feedback
- `encouraging` → empty states, "practice more" prompts, loading states

Keep it a single well-structured SVG (not multiple separate image files) so re-skinning later
is cheap.

## 3. Buttons & icons — CSS/SVG only, no downloaded icon packs

All buttons and MCQ option tiles: "clay / soft-3D" style — soft drop shadow + subtle inner
highlight + 2-color pastel gradient fill + press animation (scale down slightly, shadow
flattens on `:active`/tap).

Nav icons (home, Maths, English, back, star, settings, etc.): inline SVG, same rounded pastel
style, consistent stroke width, colors pulled from the theme tokens — not a mixed icon set.

## 4. Layout / spacing

- MCQ options: 2-column card grid of large tappable cards, not a plain list. Generous gaps
  (use spacing scale).
- Constrain content max-width on larger screens — don't stretch edge-to-edge.
- Center content vertically on screens that currently look top-heavy.
- Every screen change should visibly use the spacing scale from section 1, not ad hoc values.

## 5. Feedback animations

- **Correct:** light confetti / star-burst CSS animation + `<Mascot state="happy" />` +
  green glow on the selected option.
- **Wrong:** gentle shake on the selected option + `<Mascot state="confused" />` + soft coral
  glow (never harsh red).
- **Completion screen:** animated star count-up. Must read from the existing stars/accuracy
  logic (90%+ → 3, 70%+ → 2, 50%+ → 1) — never hardcode or duplicate these thresholds in the
  frontend; pull from wherever the backend/config already exposes them.

## 6. Background images — random placement per screen visit

Source images live at `E:\Learn with Masti\background images` (currently ~80 images).

**Build pipeline (one-time / re-run when images are added):**
- A small Node script copies/optimizes source images into `frontend/public/backgrounds/`
  (resize to max ~1600px longest side, convert to webp) and generates
  `frontend/src/backgroundManifest.js` exporting the filename list.
- Never bundle all raw images into the JS bundle — serve as static files by filename only.

**Runtime behaviour (the "surprise" element):**
On each fresh screen mount, randomly pick ONE image and ONE placement variant:
- (a) left-anchored, partially off-screen, tilt -8° to -15°
- (b) right-anchored, partially off-screen, tilt 8° to 15°
- (c) full-screen, low opacity (15-25%), solid pastel overlay on top so text stays readable, no tilt

Re-randomize on fresh navigation to a screen, not on every re-render within the same screen
(`useMemo` keyed on mount, not on state changes).

**Guardrails (non-negotiable):**
- Image must never sit behind/overlap interactive elements in a way that hurts tap accuracy
  or text contrast. Variants (a)/(b): fixed corner region, z-index below content,
  `pointer-events: none`. Variant (c): overlay must guarantee body-text contrast ratio ≥ 4.5:1.
- Load only the one selected image per screen — not all 80 upfront. `loading="lazy"` +
  200-300ms fade-in.
- This photo layer sits ON TOP OF the base pastel gradient/blob background from section 1
  tokens, not instead of it.

## 7. Non-negotiables when applying this skill

- Frontend/CSS/component changes only — never touch backend routes, schemas, validation, or
  scoring logic.
- Run the full test suite after any change and fix failures; update tests that assert on
  class names/DOM structure you intentionally changed rather than reverting the design.
- Branch off an up-to-date main (fetch + pull first) for any git work.
