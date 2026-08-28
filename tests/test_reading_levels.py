import pytest

from learn_with_masti.reading_levels import (
    MAX_RANK,
    MIN_RANK,
    DIFFICULTY_BANDS,
    QUESTION_TYPE_BANDS,
    spec_for_rank,
)


def test_difficulty_bands_cover_1_to_50_with_no_gaps_or_overlaps():
    ranks_covered = []
    for band in DIFFICULTY_BANDS:
        ranks_covered.extend(range(band.rank_min, band.rank_max + 1))
    assert ranks_covered == list(range(MIN_RANK, MAX_RANK + 1))


def test_question_type_bands_cover_1_to_50_with_no_gaps_or_overlaps():
    ranks_covered = []
    for band in QUESTION_TYPE_BANDS:
        ranks_covered.extend(range(band.rank_min, band.rank_max + 1))
    assert ranks_covered == list(range(MIN_RANK, MAX_RANK + 1))


def test_spec_for_rank_rejects_out_of_range_ranks():
    with pytest.raises(ValueError, match="between 1 and 50"):
        spec_for_rank(0)
    with pytest.raises(ValueError, match="between 1 and 50"):
        spec_for_rank(51)


@pytest.mark.parametrize(
    "rank,word_count_min,word_count_max,words_per_sentence_min,words_per_sentence_max,max_word_length",
    [
        (1, 40, 55, 5, 7, 6),
        (5, 40, 55, 5, 7, 6),
        (6, 60, 80, 7, 9, 7),
        (10, 60, 80, 7, 9, 7),
    ],
)
def test_ranks_1_to_10_are_flat_within_their_band(
    rank,
    word_count_min,
    word_count_max,
    words_per_sentence_min,
    words_per_sentence_max,
    max_word_length,
):
    spec = spec_for_rank(rank)
    assert (spec.word_count_min, spec.word_count_max) == (word_count_min, word_count_max)
    assert (spec.words_per_sentence_min, spec.words_per_sentence_max) == (
        words_per_sentence_min,
        words_per_sentence_max,
    )
    assert spec.max_word_length == max_word_length
    assert spec.question_count_min == spec.question_count_max == 7


def test_ranks_1_to_5_and_6_to_10_all_have_flat_word_count_within_their_own_band():
    ranks_1_to_5 = [spec_for_rank(r) for r in range(1, 6)]
    assert len({(s.word_count_min, s.word_count_max) for s in ranks_1_to_5}) == 1

    ranks_6_to_10 = [spec_for_rank(r) for r in range(6, 11)]
    assert len({(s.word_count_min, s.word_count_max) for s in ranks_6_to_10}) == 1


def test_rank_11_and_20_span_the_full_band_11_20_word_count_range():
    band = next(b for b in DIFFICULTY_BANDS if b.rank_min == 11)
    spec11 = spec_for_rank(11)
    spec20 = spec_for_rank(20)
    assert spec11.word_count_min == band.word_count_min
    assert spec20.word_count_max == band.word_count_max


def test_ranks_from_11_onward_are_monotonically_non_decreasing():
    prev = spec_for_rank(11)
    for rank in range(12, MAX_RANK + 1):
        spec = spec_for_rank(rank)
        assert spec.word_count_min >= prev.word_count_min
        assert spec.word_count_max >= prev.word_count_max
        assert spec.words_per_sentence_min >= prev.words_per_sentence_min
        assert spec.words_per_sentence_max >= prev.words_per_sentence_max
        prev = spec


def test_consecutive_ranks_from_11_onward_differ_only_marginally():
    """Neighbouring ranks should be barely distinguishable in word count."""
    for rank in range(11, MAX_RANK):
        a, b = spec_for_rank(rank), spec_for_rank(rank + 1)
        # Consecutive ranks' windows must touch or overlap, never leave a gap
        # and never jump by more than a handful of words.
        assert b.word_count_min <= a.word_count_max
        assert b.word_count_max - a.word_count_min <= 6


def test_rank_11_vs_rank_20_are_clearly_different():
    a, b = spec_for_rank(11), spec_for_rank(20)
    assert b.word_count_min > a.word_count_max


def test_question_types_are_cumulative_across_bands():
    types_1_10 = set(spec_for_rank(5).allowed_question_types)
    types_11_20 = set(spec_for_rank(15).allowed_question_types)
    types_21_35 = set(spec_for_rank(28).allowed_question_types)
    types_36_50 = set(spec_for_rank(45).allowed_question_types)

    assert types_1_10 == {"literal_recall"}
    assert types_1_10 < types_11_20
    assert types_11_20 < types_21_35
    assert types_21_35 < types_36_50
    assert types_36_50 == {
        "literal_recall",
        "vocabulary_in_context",
        "sequencing",
        "cause_and_effect",
        "inference",
        "main_idea",
        "authors_purpose",
        "drawing_conclusions",
    }


def test_question_type_band_boundaries_do_not_match_difficulty_band_boundaries():
    # 21-35 and 36-50 are the question-type bands; the difficulty bands at
    # that point are split 21-30/31-40 instead, deliberately not aligned.
    assert spec_for_rank(30).allowed_question_types == spec_for_rank(35).allowed_question_types
    assert spec_for_rank(35).allowed_question_types != spec_for_rank(36).allowed_question_types


def test_only_ranks_1_to_10_constrain_stem_and_option_length():
    low = spec_for_rank(3)
    assert low.stem_max_words == 9
    assert (low.option_min_words, low.option_max_words) == (1, 3)

    higher = spec_for_rank(15)
    assert higher.stem_max_words is None
    assert higher.option_min_words is None
    assert higher.option_max_words is None


@pytest.mark.parametrize(
    "rank,expected_min,expected_max",
    [
        (1, 7, 7),
        (10, 7, 7),
        (15, 7, 8),
        (25, 8, 8),
        (35, 9, 9),
        (45, 10, 10),
    ],
)
def test_question_counts_match_the_spec_per_band(rank, expected_min, expected_max):
    spec = spec_for_rank(rank)
    assert (spec.question_count_min, spec.question_count_max) == (expected_min, expected_max)


def test_words_per_sentence_is_not_narrowed_per_rank_within_a_band():
    band = next(b for b in DIFFICULTY_BANDS if b.rank_min == 11)
    spec11 = spec_for_rank(11)
    spec20 = spec_for_rank(20)
    assert (spec11.words_per_sentence_min, spec11.words_per_sentence_max) == (
        band.words_per_sentence_min,
        band.words_per_sentence_max,
    )
    assert (spec11.words_per_sentence_min, spec11.words_per_sentence_max) == (
        spec20.words_per_sentence_min,
        spec20.words_per_sentence_max,
    )


def test_words_per_sentence_bounds_are_floats():
    spec = spec_for_rank(11)
    assert isinstance(spec.words_per_sentence_min, float)
    assert isinstance(spec.words_per_sentence_max, float)


def _is_satisfiable(spec) -> bool:
    """Whether some integer (word_count, sentence_count) pair exists whose
    average words/sentence falls within the spec's range."""
    for word_count in range(spec.word_count_min, spec.word_count_max + 1):
        for sentence_count in range(1, word_count + 1):
            average = word_count / sentence_count
            if spec.words_per_sentence_min <= average <= spec.words_per_sentence_max:
                return True
    return False


@pytest.mark.parametrize("rank", range(MIN_RANK, MAX_RANK + 1))
def test_every_rank_spec_is_satisfiable_by_some_integer_word_and_sentence_count(rank):
    spec = spec_for_rank(rank)
    assert _is_satisfiable(spec), (
        f"rank {rank} has no integer (word_count, sentence_count) pair satisfying "
        f"both word_count in [{spec.word_count_min}, {spec.word_count_max}] and "
        f"words_per_sentence in [{spec.words_per_sentence_min}, {spec.words_per_sentence_max}]"
    )
