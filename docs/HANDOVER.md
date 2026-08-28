# Learn with Masti — Project Handover

Paste this into a new chat to continue work with full context.

---

## Aim

I am building an EdTech app for Indian school students, starting with **Class 3**.

**The problem:** School textbooks have very few practice questions per topic. Children who finish
early, or who are preparing for Olympiads (SOF/IMO), run out of material. Parents and teachers have
no easy way to give them more practice at the right level.

**The product:** An app with two tracks — School Syllabus and Olympiad — where a child practises
MCQs, gets instant feedback, and can ask for a step-by-step explanation when stuck. When the
pre-built question bank runs out, an LLM generates fresh questions at the same level. Progress is
tracked per child with accuracy and stars (deliberately no leaderboard — Class 3 children should not
be ranked against each other).

**Business model:** Not finalised. Two routes under consideration — B2B via school tie-ups
(dealing directly with principals) and B2C direct-to-parent subscriptions. A rough target of ₹1 Cr
revenue would need roughly 10,000–20,000 paying students at ₹500–1000/student/year. A side revenue
stream is selling printable worksheet bundles on Etsy/Gumroad, reusing the same content pipeline.

**Design principle agreed from day one:** even though this is an MVP, the architecture should be
built to scale — proper Postgres schema with indexes, UUID primary keys, aggregated progress tables,
pgvector extension pre-installed (unused for now), and config-driven behaviour so nothing needs
rewriting later.

---

## Working Style (please follow)

- I run everything through **Claude Code** in a separate terminal. Give me a single, complete,
  copy-pasteable prompt for each task rather than writing files yourself.
- After I say a task is done, **cross-check it thoroughly** — read the actual files, verify the logic
  really does what was asked, and tell me plainly if something was missed or done wrong. Several
  times a feature was reported done but was not actually implemented (a colourful worksheet design
  that came out plain, a validation layer that caught 0 out of 7 known-bad questions), so please
  verify rather than assume.
- I speak Hinglish; reply in Hinglish.
- Keep responses concise and to the point.
- Flag design or data problems early, even if I did not ask.

---

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Poetry, SQLAlchemy, Alembic
- **Database:** PostgreSQL with pgvector, running in **Podman** (not Docker) on **port 5433**
  — port 5432 is taken by a native Windows Postgres install, which caused a long debugging session
- **LLM:** Provider switch — uses Anthropic if `ANTHROPIC_API_KEY` is set, otherwise falls back to
  local **Ollama** (qwen3:1.7b / qwen3:4b) in Podman on port 11434
- **Frontend:** React (Vite) PWA, React Router
- **Project path:** `E:\Learn with Masti` (Filesystem MCP has access)
- **Tests:** pytest, ~152 passing

Four terminals run in parallel: alembic commands, uvicorn backend, `npm run dev` frontend, and
Claude Code.

---

## Features Already Built

### Auth & Accounts
- Parent signup and login (bcrypt hashing, JWT, 7-day session)
- Forgot password → reset token printed to console (real email service still pending)
- Reset password with 30-minute expiry, single use
- Multiple children per parent
- Child login via 4–6 digit PIN (separate JWT, 3-hour session, type-differentiated so a child token
  cannot access parent endpoints)
- Sign out and Switch child

### Navigation
- Subject selection screen (Maths / English)
- Maths path: track (School/Olympiad) → topic → level → practice
- English path: passage list → passage reading

### Maths Practice
- Topics: Addition, Subtraction, Multiplication
- School track levels: Easy / Medium / Hard. Olympiad track levels: Super Hard / Pro
- MCQ with 4 options, instant green/red feedback
- "Show me how" → LLM step-by-step solution in Class-3-friendly language
- "Practice More" → LLM generates fresh questions (currently very slow on local Qwen)
- Difficulty progression easy → medium → hard, shuffled within each level

### English Comprehension
- Passages stored in the database, listed in difficulty_rank order
- Passage stays visible above the questions while the child answers
- MCQ questions, with the explanation hint revealed on a wrong answer
- Completion summary: score, accuracy %, stars, encouragement varying with score, Retry and
  Next Passage buttons
- Previous / Next passage navigation by rank, disabled at the ends
- A measurable 50-rank difficulty ladder defined in `reading_levels.py` — word count, words per
  sentence, maximum word length in letters, question count, and which question types each band
  allows (literal recall only at the bottom, rising through vocabulary-in-context, sequencing,
  cause-and-effect, inference, main idea, author's purpose)
- 4 hand-written seeded passages at ranks 1, 5, 25 and 50, all validated clean

### Progress Tracking
- Every attempt persisted to Postgres (not localStorage), so it syncs across devices
- Maths: per topic/track accuracy and stars
- English: aggregate row plus per-passage history showing title, level, score, accuracy, stars and
  last-read date
- Stars: 90%+ → 3, 70%+ → 2, 50%+ → 1. No leaderboard by design.

### Question Quality Pipeline
- **Stage 1 — programmatic validation** (`validation.py`): arithmetic correctness, exactly one
  correct option, explanation-hint consistency (catches self-contradictory hints), digit rules
  (multiplication single-digit 1–9, addition/subtraction 2–3 digits), operation matches declared
  topic, duplicate options, duplicate question text, letter-option resolution, and exclusion of
  derived intermediate values from digit checks
- **Stage 2 — LLM reviewer**: separate provider selection with its own models
  (`claude-sonnet-4-6` or `qwen3:4b` with thinking enabled), checking mathematical correctness,
  single correct answer, distractor plausibility, Class 3 age-appropriateness, whether the difficulty
  label genuinely matches the content, clarity, and internal consistency
- `validate_passage` for English checking a passage against its rank spec
- `scripts/audit_questions.py` CLI with a `--review` flag

### Content Tools
- `scripts/generate_worksheet.py` — printable A4 PDF worksheets. All arithmetic is generated
  programmatically and the answer key computed from the same values, so answers are always correct.
  Illustrated kid-friendly layout drawn entirely with reportlab shapes (owl mascot, balloons, clouds,
  grass strip, pastel palette, stars box) — no stock images, so there is no licensing risk when
  selling on Etsy. CLI flags: `--topic`, `--set`, `--seed`, `--out`.
- `scripts/seed_english_passages.py` — validates before inserting, refuses to seed invalid content

---

## Pending Work

### Content
1. **Generate the remaining 46 English passages** (ranks 2–4, 6–24, 26–49) through the validation +
   review pipeline. The 4 samples exist to judge the ladder first.
2. **Clean the Maths question bank.** It holds ~450 questions of which **51 are flagged** by stage-1
   validation. These were bulk-generated without review and include wrong answers, self-contradictory
   hints, duplicates, addition questions filed under multiplication, single-digit rule violations,
   and trivial questions labelled Olympiad-level. An overnight `--review` audit was started but the
   results were never checked.
3. **More Maths topics** — shapes, patterns, measurement, division.

### Performance (blocking)
4. **"Practice More" is effectively unusable** — local Qwen on CPU takes 5–10+ minutes and often
   times out. The agreed fix is **background generation with DB persistence**: run generation offline
   (thinking mode on, quality high), validate and review it, save approved questions to the database,
   and have the child's "Practice More" serve instantly from that pool. Live LLM calls should only
   happen as a rare fallback. Generated questions are currently discarded entirely — nothing is saved.

### Features
5. **Gamification** — mascot with expressions (happy / confused / encouraging), balloon-pop answer
   game, timed challenge mode, sticker or star rewards. Content and backend were deliberately built
   first so this layer can sit on top without rework.
6. **Timed / scored test mode** — the schema already has `mode: "scored" | "open"`, but only "open"
   is used today.
7. **Creative writing** — picture composition (child writes 5–7 sentences about an image),
   paragraph writing, story writing, letter writing, diary entry. This needs generated or licensed
   images, subjective LLM feedback rather than MCQ checking, and a new text-input UI, so it was
   deliberately sequenced last.
8. **Email service** for password reset — currently the token only prints to the backend console.

### Business / Brand
9. **Brand name and logo not decided.** "Learn with Masti" is the working name. Since the same brand
   should serve both the Indian app audience and global Etsy buyers, a Hindi-rooted name was ruled
   out. Directions explored: owl-mascot names, and more mature subject-neutral options such as
   Chalk & Compass, Lanterna, The Learning Loft. Nothing chosen yet. Before finalising, check Etsy
   handle availability, domain availability, and run a trademark search on ipindiaonline.gov.in.
10. **Decide B2B (schools) vs B2C (parents)** go-to-market, and pricing.
11. **Production deployment** — the plan discussed was a managed Postgres (Azure Database for
    PostgreSQL Flexible Server) rather than a self-hosted container, and baking the Ollama model into
    a custom image at build time so no runtime download is needed. This was explained but I said I
    would revisit it later, so it needs re-explaining when the time comes.

### Known Small Issues
- Star thresholds (90/70/50) are duplicated in both `config.py` and `PassagePage.jsx`. If the backend
  values change, the frontend will silently disagree. A small `/config` endpoint would fix this.
- `TOPIC_SYMBOLS` in `generate_worksheet.py` is dead code.
- Worth confirming the answer-key page title does not overlap the header balloons for longer topic
  names.
- Branch state needs verifying — `scripts/audit_questions.py` went missing from the working tree at
  one point after a branch switch, so confirm the `question-quality-validation` and
  `printable-worksheets` branches both hold the right work and were pushed.

---

## Suggested Next Step

Highest value first: **background question generation with database persistence**. It fixes the
broken "Practice More" experience, makes the review pipeline's output reusable instead of throwaway,
cuts compute cost, and is a prerequisite for generating the remaining English passages at scale.
