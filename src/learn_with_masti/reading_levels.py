"""The English reading-comprehension difficulty ladder, as a measurable spec.

"Gradually tougher" only means something if it can be checked, so every rule
here is a number a passage/question can be validated against -- word counts,
sentence lengths, letter counts, question counts, and allowed question
types -- rather than a difficulty label. Passage generation and passage
validation are both meant to read their targets from this module (via
spec_for_rank), so they can never drift apart.

Ranks 1-50 are grouped into two independent partitions:
- DIFFICULTY_BANDS: prose/length targets (word count, words/sentence, max
  word length, question count). Only word_count is narrowed per rank: ranks
  1-10 are flat within their band (any passage in that band uses the same
  range), and from rank 11 on, spec_for_rank narrows word_count to a small
  per-rank slice, so neighbouring ranks are barely distinguishable but the
  two ends of a ten-rank span clearly are. words_per_sentence is deliberately
  NOT sliced per rank -- it stays at the band's full range for every rank in
  that band, compared as a float average (total_words / total_sentences,
  essentially never a whole number) rather than rounded to an integer range;
  narrowing both word_count and words_per_sentence independently per rank
  can make a rank's spec unsatisfiable, since a narrow word_count slice may
  admit no integer sentence count whose average falls inside an equally
  narrow words_per_sentence slice.
- QUESTION_TYPE_BANDS: which question types are allowed, cumulative as rank
  increases. Its boundaries (1-10/11-20/21-35/36-50) do not line up with the
  difficulty bands above -- they are a separate axis of difficulty.
"""

from dataclasses import dataclass
from typing import Literal

QuestionType = Literal[
    "literal_recall",
    "vocabulary_in_context",
    "sequencing",
    "cause_and_effect",
    "inference",
    "main_idea",
    "authors_purpose",
    "drawing_conclusions",
]

MIN_RANK = 1
MAX_RANK = 50


@dataclass(frozen=True)
class DifficultyBand:
    rank_min: int
    rank_max: int
    word_count_min: int
    word_count_max: int
    words_per_sentence_min: int
    words_per_sentence_max: int
    max_word_length: int
    question_count_min: int
    question_count_max: int
    notes: str = ""


# Ranks 1-10 stay flat within their band (no per-rank narrowing); from rank
# 11 on, spec_for_rank() interpolates a small slice of each range per rank.
DIFFICULTY_BANDS: tuple[DifficultyBand, ...] = (
    DifficultyBand(
        rank_min=1,
        rank_max=5,
        word_count_min=40,
        word_count_max=55,
        words_per_sentence_min=5,
        words_per_sentence_max=7,
        max_word_length=6,
        question_count_min=7,
        question_count_max=7,
        notes=(
            "For a child who genuinely struggles with English. Simple present "
            "or simple past only, one idea per sentence, no clauses, no dialogue."
        ),
    ),
    DifficultyBand(
        rank_min=6,
        rank_max=10,
        word_count_min=60,
        word_count_max=80,
        words_per_sentence_min=7,
        words_per_sentence_max=9,
        max_word_length=7,
        question_count_min=7,
        question_count_max=7,
    ),
    DifficultyBand(
        rank_min=11,
        rank_max=20,
        word_count_min=85,
        word_count_max=110,
        words_per_sentence_min=9,
        words_per_sentence_max=11,
        max_word_length=8,
        question_count_min=7,
        question_count_max=8,
    ),
    DifficultyBand(
        rank_min=21,
        rank_max=30,
        word_count_min=110,
        word_count_max=140,
        words_per_sentence_min=11,
        words_per_sentence_max=13,
        max_word_length=9,
        question_count_min=8,
        question_count_max=8,
    ),
    DifficultyBand(
        rank_min=31,
        rank_max=40,
        word_count_min=140,
        word_count_max=170,
        words_per_sentence_min=13,
        words_per_sentence_max=15,
        max_word_length=10,
        question_count_min=9,
        question_count_max=9,
    ),
    DifficultyBand(
        rank_min=41,
        rank_max=50,
        word_count_min=170,
        word_count_max=200,
        words_per_sentence_min=15,
        words_per_sentence_max=17,
        max_word_length=11,
        question_count_min=10,
        question_count_max=10,
    ),
)


@dataclass(frozen=True)
class QuestionTypeBand:
    rank_min: int
    rank_max: int
    allowed_question_types: tuple[QuestionType, ...]
    # Only ranks 1-10 constrain stem/option length; None means unconstrained.
    stem_max_words: int | None = None
    option_min_words: int | None = None
    option_max_words: int | None = None


# Cumulative: each band's allowed_question_types includes every type from the
# bands before it, plus whatever that band adds.
QUESTION_TYPE_BANDS: tuple[QuestionTypeBand, ...] = (
    QuestionTypeBand(
        rank_min=1,
        rank_max=10,
        allowed_question_types=("literal_recall",),
        stem_max_words=9,
        option_min_words=1,
        option_max_words=3,
    ),
    QuestionTypeBand(
        rank_min=11,
        rank_max=20,
        allowed_question_types=("literal_recall", "vocabulary_in_context", "sequencing"),
    ),
    QuestionTypeBand(
        rank_min=21,
        rank_max=35,
        allowed_question_types=(
            "literal_recall",
            "vocabulary_in_context",
            "sequencing",
            "cause_and_effect",
            "inference",
        ),
    ),
    QuestionTypeBand(
        rank_min=36,
        rank_max=50,
        allowed_question_types=(
            "literal_recall",
            "vocabulary_in_context",
            "sequencing",
            "cause_and_effect",
            "inference",
            "main_idea",
            "authors_purpose",
            "drawing_conclusions",
        ),
    ),
)


@dataclass(frozen=True)
class RankSpec:
    """The full measurable target for one difficulty_rank (1-50)."""

    rank: int
    word_count_min: int
    word_count_max: int
    # Floats, not ints: a passage's actual words/sentence is an average
    # (total_words / total_sentences), essentially never a whole number, so
    # it must be compared as one rather than rounded to an integer range.
    words_per_sentence_min: float
    words_per_sentence_max: float
    max_word_length: int
    question_count_min: int
    question_count_max: int
    allowed_question_types: tuple[QuestionType, ...]
    stem_max_words: int | None
    option_min_words: int | None
    option_max_words: int | None
    notes: str


def _band_for_rank(rank: int) -> DifficultyBand:
    for band in DIFFICULTY_BANDS:
        if band.rank_min <= rank <= band.rank_max:
            return band
    raise ValueError(f"difficulty_rank must be between {MIN_RANK} and {MAX_RANK}, got {rank}")


def _question_type_band_for_rank(rank: int) -> QuestionTypeBand:
    for band in QUESTION_TYPE_BANDS:
        if band.rank_min <= rank <= band.rank_max:
            return band
    raise ValueError(f"difficulty_rank must be between {MIN_RANK} and {MAX_RANK}, got {rank}")


def _rank_slice(rank: int, rank_min: int, rank_max: int, lo: int, hi: int) -> tuple[int, int]:
    """Partition [lo, hi] into one equal-width slice per rank in
    [rank_min, rank_max] and return the slice for `rank`.

    This is what makes ranks 11+ "marginally harder than the one before":
    consecutive ranks get adjacent (barely different) slices, while the
    band's first and last ranks span its full width.
    """
    band_size = rank_max - rank_min + 1
    idx = rank - rank_min
    step = (hi - lo) / band_size
    slice_lo = lo if idx == 0 else round(lo + step * idx)
    slice_hi = hi if idx == band_size - 1 else round(lo + step * (idx + 1))
    return (slice_lo, slice_hi)


def spec_for_rank(rank: int) -> RankSpec:
    """The measurable target spec for one passage difficulty_rank (1-50)."""
    if not (MIN_RANK <= rank <= MAX_RANK):
        raise ValueError(f"difficulty_rank must be between {MIN_RANK} and {MAX_RANK}, got {rank}")

    band = _band_for_rank(rank)
    if rank <= 10:
        word_count_range = (band.word_count_min, band.word_count_max)
    else:
        word_count_range = _rank_slice(
            rank, band.rank_min, band.rank_max, band.word_count_min, band.word_count_max
        )

    # words_per_sentence is NOT sliced per rank -- it stays at the band's
    # full range for every rank in that band. word_count alone carries the
    # per-rank progression; narrowing both independently can make a rank's
    # spec unsatisfiable (e.g. a word_count slice with no integer sentence
    # count whose average falls inside an equally-narrowed sentence-length
    # slice).
    qtype_band = _question_type_band_for_rank(rank)
    return RankSpec(
        rank=rank,
        word_count_min=word_count_range[0],
        word_count_max=word_count_range[1],
        words_per_sentence_min=float(band.words_per_sentence_min),
        words_per_sentence_max=float(band.words_per_sentence_max),
        max_word_length=band.max_word_length,
        question_count_min=band.question_count_min,
        question_count_max=band.question_count_max,
        allowed_question_types=qtype_band.allowed_question_types,
        stem_max_words=qtype_band.stem_max_words,
        option_min_words=qtype_band.option_min_words,
        option_max_words=qtype_band.option_max_words,
        notes=band.notes,
    )
