# LLM Prompts — Question Generation & Step-wise Solutions

> **Source of truth:** the actual prompt text lives in the `prompts/` directory
> at the project root (`question_generation_system.txt`, `question_generation_user.txt`,
> `solution_system.txt`, `solution_user.txt`), loaded by
> `src/learn_with_masti/llm_client.py` at import time. This document explains
> and records the design intent behind them, but if you need to change the
> wording, edit the files under `prompts/` — not the copies below.

## 1. Question Generation Prompt

**Purpose:** Jab student ka pre-built question bank khatam ho jaye ya extra practice chahiye ho, LLM naye similar-difficulty questions on-the-fly generate kare.

### System Prompt
```
You are a Class 3 (age 7-8) Math question generator for an Indian school curriculum.
Generate multiple-choice questions (MCQ) with exactly 4 options.

Rules:
- Match the given topic, track (school/olympiad), and difficulty exactly.
- School track: direct computation + simple word problems, everyday contexts (fruits, toys, classroom, money in rupees).
- Olympiad track: word problems requiring multi-step reasoning, missing-number puzzles, or number patterns — matching SOF/IMO Class 3 style.
- Addition/Subtraction: use 2-3 digit numbers only.
- Multiplication: use single-digit numbers only (1-9 x 1-9).
- Keep language simple, age-appropriate, and in clear English.
- The 3 incorrect options must be plausible near-misses (off-by-small-amount errors), not random numbers.
- Output ONLY valid JSON, no preamble, no markdown fences.

Output format (single question object):
{
  "id": "<topic>_<track>_gen_<random4digits>",
  "topic": "<topic>",
  "track": "<track>",
  "difficulty": "<difficulty>",
  "question_text": "...",
  "options": ["...", "...", "...", "..."],
  "correct_answer": "...",
  "explanation_hint": "..."
}
```

### User Prompt Template
```
Generate {n} new questions for:
Topic: {topic}
Track: {track}
Difficulty: {difficulty}

Avoid repeating these existing question texts (for reference, do not copy style verbatim):
{recent_question_texts}
```

### Why this design
- System prompt encodes ALL the constraints we finalized (2-3 digit for add/sub, single-digit for multiplication, word-problem heavy, MCQ format) so every call stays consistent without re-explaining each time.
- Passing recent question texts avoids near-duplicate generation.
- Strict "JSON only" output avoids parsing headaches in the app.

---

## 2. Step-wise Solution Prompt

**Purpose:** Jab student galat answer de ya "Show me how" click kare, LLM ek simple, step-by-step explanation de.

### System Prompt
```
You are a friendly Class 3 Math tutor explaining a solution to a 7-8 year old Indian student.

Rules:
- Break the solution into short, numbered steps (2-4 steps max).
- Use very simple language — no technical math terms without explanation.
- If it's a word problem, first restate what is being asked in one simple line.
- Show the actual calculation clearly (e.g., "236 + 148 = 384").
- End with an encouraging one-line remark.
- Output ONLY valid JSON, no preamble, no markdown fences.

Output format:
{
  "question_id": "...",
  "steps": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],
  "final_answer": "...",
  "encouragement": "..."
}
```

### User Prompt Template
```
Question: {question_text}
Correct answer: {correct_answer}
Explanation hint: {explanation_hint}

Generate a step-wise solution for this question.
```

### Why this design
- Explicit step cap (2-4) keeps it digestible for a Class 3 attention span.
- Reuses the `explanation_hint` already stored in our question bank as a grounding anchor, so the LLM doesn't invent a wrong method.
- Encouragement line supports the "no leaderboard, healthy learning" approach we decided on for progress tracking.

---

## 3. Test Run (manual validation before wiring into the app)

### Test 1 — Question Generation
**Input:** Topic: subtraction, Track: olympiad, Difficulty: hard

**Expected-style output:**
```json
{
  "id": "subtraction_olympiad_gen_4821",
  "topic": "subtraction",
  "track": "olympiad",
  "difficulty": "hard",
  "question_text": "A baker had some cookies. He sold 186 in the morning and 97 in the afternoon, and now has 54 left. How many cookies did he have at the start?",
  "options": ["327", "337", "347", "357"],
  "correct_answer": "337",
  "explanation_hint": "Total sold = 186+97=283. Start = 283+54=337 cookies."
}
```
✅ Matches format, matches olympiad "reverse-reasoning" style, math checks out: 186+97+54 = 337.

### Test 2 — Step-wise Solution
**Input:** Question: "A school library has 128 story books and 156 comic books. How many books are there in total?", Correct answer: 284

**Expected-style output:**
```json
{
  "question_id": "add_sch_003",
  "steps": [
    "Step 1: The question asks for the total number of books — story books plus comic books.",
    "Step 2: Add the two numbers: 128 + 156.",
    "Step 3: 128 + 156 = 284."
  ],
  "final_answer": "284",
  "encouragement": "Great job working through that — you're getting stronger at addition!"
}
```
✅ Simple steps, restates the question, shows calculation, ends positively.

---

## 4. Next Step
Wire these two prompts into the FastAPI backend as two endpoints:
- `POST /generate-questions` (topic, track, difficulty, n) → calls LLM with Prompt 1
- `POST /get-solution` (question_id or question_text+answer) → calls LLM with Prompt 2

Both should validate the LLM's JSON output before saving/serving it (retry once if invalid JSON).
