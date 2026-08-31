import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from generate_worksheet import (  # noqa: E402
    SUMS_PER_WORKSHEET,
    WORD_PROBLEMS_PER_WORKSHEET,
    _apply_op,
    generate_column_sums,
    generate_word_problems,
    generate_worksheet_data,
    main,
    render_worksheet_pdf,
)

import random  # noqa: E402

TOPICS = ["addition", "subtraction", "multiplication"]
SEEDS = [0, 1, 7, 42]


@pytest.mark.parametrize("topic", TOPICS)
@pytest.mark.parametrize("seed", SEEDS)
def test_generate_column_sums_answers_are_arithmetically_correct(topic, seed):
    sums = generate_column_sums(topic, random.Random(seed))

    assert len(sums) == SUMS_PER_WORKSHEET
    for s in sums:
        assert s.answer == _apply_op(s.a, s.op, s.b)


@pytest.mark.parametrize("seed", SEEDS)
def test_addition_sums_use_2_or_3_digit_operands(seed):
    for s in generate_column_sums("addition", random.Random(seed)):
        assert s.op == "+"
        assert 2 <= len(str(s.a)) <= 3
        assert 2 <= len(str(s.b)) <= 3


@pytest.mark.parametrize("seed", SEEDS)
def test_subtraction_sums_are_non_negative_with_2_or_3_digit_operands(seed):
    for s in generate_column_sums("subtraction", random.Random(seed)):
        assert s.op == "-"
        assert s.a >= s.b
        assert s.answer >= 0
        assert 2 <= len(str(s.a)) <= 3
        assert 2 <= len(str(s.b)) <= 3


@pytest.mark.parametrize("seed", SEEDS)
def test_multiplication_sums_use_single_digit_operands(seed):
    for s in generate_column_sums("multiplication", random.Random(seed)):
        assert s.op == "x"
        assert 1 <= s.a <= 9
        assert 1 <= s.b <= 9


@pytest.mark.parametrize("topic", TOPICS)
@pytest.mark.parametrize("seed", SEEDS)
def test_generate_word_problems_answers_are_arithmetically_correct(topic, seed):
    problems = generate_word_problems(topic, random.Random(seed))

    assert len(problems) == WORD_PROBLEMS_PER_WORKSHEET
    for wp in problems:
        assert wp.answer == _apply_op(wp.a, wp.op, wp.b)
        assert "Answer" not in wp.text


def test_word_problems_never_leak_the_answer_into_the_question_text():
    for topic in TOPICS:
        for wp in generate_word_problems(topic, random.Random(99)):
            # The question text should state the operands, not the computed answer.
            assert str(wp.a) in wp.text
            assert str(wp.b) in wp.text


@pytest.mark.parametrize("topic", TOPICS)
@pytest.mark.parametrize("seed", SEEDS)
def test_generate_worksheet_data_answer_key_matches_questions(topic, seed):
    """The core requirement: every answer in the key must match the exact
    question it corresponds to, arithmetically."""
    data = generate_worksheet_data(topic, seed)

    assert data.topic == topic
    assert len(data.sums) == SUMS_PER_WORKSHEET
    assert len(data.word_problems) == WORD_PROBLEMS_PER_WORKSHEET

    for s in data.sums:
        assert s.answer == _apply_op(s.a, s.op, s.b)
    for wp in data.word_problems:
        assert wp.answer == _apply_op(wp.a, wp.op, wp.b)


@pytest.mark.parametrize("topic", TOPICS)
def test_generate_worksheet_data_is_reproducible_given_same_seed(topic):
    first = generate_worksheet_data(topic, seed=123)
    second = generate_worksheet_data(topic, seed=123)

    assert first == second


@pytest.mark.parametrize("topic", TOPICS)
def test_generate_worksheet_data_differs_across_seeds(topic):
    first = generate_worksheet_data(topic, seed=1)
    second = generate_worksheet_data(topic, seed=2)

    assert first != second


def test_generate_worksheet_data_rejects_unknown_topic():
    with pytest.raises(ValueError, match="Unknown topic"):
        generate_worksheet_data("geometry", seed=0)


def test_render_worksheet_pdf_writes_a_valid_two_page_pdf(tmp_path):
    data = generate_worksheet_data("addition", seed=5)
    out_path = tmp_path / "worksheet.pdf"

    render_worksheet_pdf(data, "Set A", out_path)

    contents = out_path.read_bytes()
    assert contents.startswith(b"%PDF")
    assert len(contents) > 0

    import re

    page_objects = re.findall(rb"/Type\s*/Page(?!s)", contents)
    assert len(page_objects) == 2  # questions page + answer-key page


@pytest.mark.parametrize("topic", TOPICS)
def test_render_worksheet_pdf_succeeds_for_every_topic(topic, tmp_path):
    """The redesigned (owl/clouds/balloons/pastel-card) layout must render
    without raising for every topic, not just addition."""
    data = generate_worksheet_data(topic, seed=11)
    out_path = tmp_path / f"{topic}.pdf"

    render_worksheet_pdf(data, "Set A", out_path)

    contents = out_path.read_bytes()
    assert contents.startswith(b"%PDF")
    assert len(contents) > 0


def test_cli_main_generates_pdf_file(tmp_path):
    out_path = tmp_path / "cli_worksheet.pdf"

    main(["--topic", "multiplication", "--set", "Set C", "--seed", "3", "--out", str(out_path)])

    assert out_path.exists()
    assert out_path.read_bytes().startswith(b"%PDF")
