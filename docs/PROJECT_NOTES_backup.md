# Learn with Masti — Project Notes

## Vision
EdTech app for school students, starting with **Class 3, Math only**.
Solves the problem of limited practice questions in school textbooks — provides extra practice for both:
- **School Syllabus** track
- **Olympiad (SOF/IMO) prep** track

## Business Model (TBD)
- Distribution: School tie-ups (principal dealing) vs Direct-to-parent (B2C) — not finalized yet
- Monetization: subscription-based likely, exact pricing TBD
- Target scale discussed: ~1 Cr revenue would need ~10,000–20,000 paying students at ₹500–1000/student/year

## MVP Scope (Confirmed)
1. **Login/signup system** — student (+ maybe parent) account
2. **Tap-based topic selection** — School Syllabus / Olympiad track, topic tiles
3. **MCQ-based practice** — 4 options, instant feedback (not numeric input, per latest decision)
4. **Progress tracking** — topics completed, accuracy %, stars/badges (NOT a competitive leaderboard — avoid anxiety for Class 3 kids)
5. **"Practice More" (LLM generation)** — when question bank runs low, LLM generates fresh similar-difficulty questions
6. **Step-wise solutions (LLM)** — simple, Class 3-appropriate language, triggered on wrong answer or "Show me how"
7. **Two modes**: Scored/evaluation sets (fixed, saved) vs Open practice sets (unlimited, unscored)

## Gamification (Phase 2 — after backend/content works)
- Balloon-pop game (tap correct-answer balloon)
- Timed challenge mode (e.g., 30-sec sprints, speed + accuracy tracked)
- Friendly mascot/character-driven MCQ UI with reactions
- Reward system: stars/stickers per topic completed (not leaderboard)

**Build order rationale:** content + backend logic first, gamified UI layer last — avoids rework.

## Phase 1: Starting Topics (Content First Approach)
Starting topics (single-digit level):
- **Addition**
- **Subtraction**
- **Multiplication (single-digit)**

Question format: **MCQ (4 options)**

### Content targets per topic (starting bank size)
- 15 School-level questions
- 10 Olympiad-level questions (word problems, pattern-based, multi-step)

### Question JSON structure
```json
{
  "id": "...",
  "topic": "addition" / "subtraction" / "multiplication",
  "track": "school" / "olympiad",
  "difficulty": "easy" / "medium" / "hard",
  "question_text": "...",
  "options": ["...", "...", "...", "..."],
  "correct_answer": "...",
  "explanation_hint": "..."
}
```

## Build Sequence
1. ✅ Decide scope & features
2. ⏳ Create seed question bank (Addition, Subtraction, Multiplication — school + olympiad)
3. ⏳ Design & test LLM prompt for generating new questions (standalone test before integration)
4. ⏳ Design & test LLM prompt for step-wise solutions
5. ⏳ Wire up basic script/prototype (topic → question → check answer → generate more / solution)
6. ⏳ Add login, scoring, progress tracking
7. ⏳ Add gamified UI (balloon game, timer, mascot)

## Open Decisions
- School tie-up vs direct-to-parent go-to-market
- Exact pricing/monetization
- Which specific Class 3 topics beyond addition/subtraction/multiplication (shapes, patterns, measurement, etc.)
