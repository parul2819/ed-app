import json
import logging
from types import SimpleNamespace

import httpx
import pytest
from pydantic import ValidationError

import learn_with_masti.llm_client as llm_client
from learn_with_masti.config import PROMPTS_DIR
from learn_with_masti.llm_client import (
    AnthropicProvider,
    QwenProvider,
    _load_prompt,
    _parse_json,
    _strip_think_block,
)


def test_prompts_are_loaded_from_files():
    assert llm_client.QUESTION_GENERATION_SYSTEM_PROMPT.startswith(
        "You are a Class 3 (age 7-8) Math question generator"
    )
    assert "{topic}" in llm_client.QUESTION_GENERATION_USER_TEMPLATE
    assert "{n}" in llm_client.QUESTION_GENERATION_USER_TEMPLATE
    assert llm_client.SOLUTION_SYSTEM_PROMPT.startswith(
        "You are a friendly Class 3 Math tutor"
    )
    assert "{question_text}" in llm_client.SOLUTION_USER_TEMPLATE
    assert "{correct_answer}" in llm_client.SOLUTION_USER_TEMPLATE
    assert llm_client.QUESTION_REVIEW_SYSTEM_PROMPT.startswith(
        "You are a strict quality reviewer"
    )
    assert "{question_text}" in llm_client.QUESTION_REVIEW_USER_TEMPLATE
    assert "{correct_answer}" in llm_client.QUESTION_REVIEW_USER_TEMPLATE


def test_load_prompt_reads_file_contents():
    content = _load_prompt("solution_user.txt")

    assert content == (PROMPTS_DIR / "solution_user.txt").read_text(
        encoding="utf-8"
    ).rstrip("\n")


def test_load_prompt_raises_clear_error_when_file_missing():
    with pytest.raises(FileNotFoundError, match="does_not_exist.txt"):
        _load_prompt("does_not_exist.txt")


def test_get_provider_defaults_to_anthropic_when_key_set(monkeypatch):
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(llm_client, "ANTHROPIC_API_KEY", "sk-test-key")

    provider = llm_client.get_provider()

    assert provider is llm_client._anthropic_provider


def test_get_provider_falls_back_to_qwen_when_key_missing(monkeypatch):
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(llm_client, "ANTHROPIC_API_KEY", None)

    provider = llm_client.get_provider()

    assert provider is llm_client._qwen_provider


def test_get_provider_returns_qwen_when_explicitly_selected(monkeypatch):
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "qwen")
    monkeypatch.setattr(llm_client, "ANTHROPIC_API_KEY", "sk-test-key")

    provider = llm_client.get_provider()

    assert provider is llm_client._qwen_provider


def test_get_review_provider_defaults_to_anthropic_when_key_set(monkeypatch):
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(llm_client, "ANTHROPIC_API_KEY", "sk-test-key")

    provider = llm_client.get_review_provider()

    assert provider is llm_client._anthropic_review_provider


def test_get_review_provider_falls_back_to_qwen_when_key_missing(monkeypatch):
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(llm_client, "ANTHROPIC_API_KEY", None)

    provider = llm_client.get_review_provider()

    assert provider is llm_client._qwen_review_provider


def test_get_review_provider_returns_qwen_when_explicitly_selected(monkeypatch):
    monkeypatch.setattr(llm_client, "LLM_PROVIDER", "qwen")
    monkeypatch.setattr(llm_client, "ANTHROPIC_API_KEY", "sk-test-key")

    provider = llm_client.get_review_provider()

    assert provider is llm_client._qwen_review_provider


def test_review_provider_singletons_use_review_specific_models():
    assert llm_client._anthropic_review_provider._model == llm_client.ANTHROPIC_REVIEW_MODEL
    assert llm_client._qwen_review_provider._model == llm_client.OLLAMA_REVIEW_MODEL
    assert llm_client._qwen_review_provider._think is True
    assert llm_client._qwen_provider._think is False


async def test_anthropic_provider_complete_returns_concatenated_text(monkeypatch):
    provider = AnthropicProvider()

    received_kwargs = {}

    async def fake_create(**kwargs):
        received_kwargs.update(kwargs)
        return SimpleNamespace(
            content=[
                SimpleNamespace(type="text", text="hello "),
                SimpleNamespace(type="text", text="world"),
            ]
        )

    fake_client = SimpleNamespace(messages=SimpleNamespace(create=fake_create))
    monkeypatch.setattr(provider, "_get_client", lambda: fake_client)

    result = await provider.complete("sys prompt", "user prompt")

    assert result == "hello world"
    assert received_kwargs["system"] == "sys prompt"
    assert received_kwargs["messages"] == [{"role": "user", "content": "user prompt"}]


async def test_anthropic_provider_complete_skips_non_text_blocks(monkeypatch):
    provider = AnthropicProvider()

    async def fake_create(**kwargs):
        return SimpleNamespace(
            content=[
                SimpleNamespace(type="tool_use", text="ignored"),
                SimpleNamespace(type="text", text="kept"),
            ]
        )

    fake_client = SimpleNamespace(messages=SimpleNamespace(create=fake_create))
    monkeypatch.setattr(provider, "_get_client", lambda: fake_client)

    result = await provider.complete("sys prompt", "user prompt")

    assert result == "kept"


async def test_qwen_provider_complete_calls_ollama_chat_endpoint(monkeypatch):
    monkeypatch.setattr(llm_client, "OLLAMA_BASE_URL", "http://fake-ollama:11434")
    monkeypatch.setattr(llm_client, "OLLAMA_MODEL", "qwen3:4b")

    captured = {}

    class _FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": "qwen reply"}}

    class _FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            captured["init_kwargs"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc_info):
            return False

        async def post(self, url, json):
            captured["url"] = url
            captured["json"] = json
            return _FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)

    provider = QwenProvider()
    result = await provider.complete("sys prompt", "user prompt")

    assert result == "qwen reply"
    assert captured["init_kwargs"]["base_url"] == "http://fake-ollama:11434"
    assert captured["url"] == "/api/chat"
    assert captured["json"]["model"] == "qwen3:4b"
    assert captured["json"]["stream"] is False
    assert captured["json"]["think"] is False
    assert captured["json"]["messages"] == [
        {"role": "system", "content": "sys prompt"},
        {"role": "user", "content": "user prompt"},
    ]


async def test_qwen_provider_review_instance_sends_think_true_and_review_model(
    monkeypatch,
):
    captured = {}

    class _FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": "qwen review reply"}}

    class _FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc_info):
            return False

        async def post(self, url, json):
            captured["json"] = json
            return _FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)

    provider = QwenProvider(model="qwen3:4b", think=True)
    result = await provider.complete("sys prompt", "user prompt")

    assert result == "qwen review reply"
    assert captured["json"]["model"] == "qwen3:4b"
    assert captured["json"]["think"] is True


async def test_anthropic_provider_uses_custom_model_when_given(monkeypatch):
    received_kwargs = {}

    async def fake_create(**kwargs):
        received_kwargs.update(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text="ok")])

    provider = AnthropicProvider(model="claude-sonnet-4-6")
    fake_client = SimpleNamespace(messages=SimpleNamespace(create=fake_create))
    monkeypatch.setattr(provider, "_get_client", lambda: fake_client)

    await provider.complete("sys prompt", "user prompt")

    assert received_kwargs["model"] == "claude-sonnet-4-6"


def test_strip_think_block_removes_leading_think_tag():
    text = "<think>let me reason about this...</think>{\"final_answer\": \"60\"}"

    assert _strip_think_block(text) == '{"final_answer": "60"}'


def test_strip_think_block_handles_multiline_reasoning_and_surrounding_whitespace():
    text = "  <think>\nstep 1\nstep 2\n</think>\n\n{\"ok\": true}"

    assert _strip_think_block(text) == '{"ok": true}'


def test_strip_think_block_leaves_text_without_think_tag_unchanged():
    text = '{"final_answer": "60"}'

    assert _strip_think_block(text) == text


def test_strip_think_block_only_strips_leading_block():
    text = '<think>reasoning</think>{"note": "the word think appears in <think> here too"}'

    assert _strip_think_block(text) == (
        '{"note": "the word think appears in <think> here too"}'
    )


async def test_qwen_provider_complete_strips_think_block_from_response(monkeypatch):
    class _FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "message": {
                    "content": "<think>reasoning about the answer</think>{\"ok\": true}"
                }
            }

    class _FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc_info):
            return False

        async def post(self, url, json):
            return _FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)

    provider = QwenProvider()
    result = await provider.complete("sys prompt", "user prompt")

    assert result == '{"ok": true}'


def test_parse_json_handles_single_object():
    parsed = _parse_json('{"final_answer": "60"}')

    assert parsed == {"final_answer": "60"}


def test_parse_json_handles_proper_array():
    parsed = _parse_json('[{"id": "1"}, {"id": "2"}]')

    assert parsed == [{"id": "1"}, {"id": "2"}]


def test_parse_json_handles_concatenated_objects():
    raw_text = '{"id": "1"}\n{"id": "2"}\n{"id": "3"}'

    parsed = _parse_json(raw_text)

    assert parsed == [{"id": "1"}, {"id": "2"}, {"id": "3"}]


def test_parse_json_handles_concatenated_objects_with_code_fences():
    raw_text = '```json\n{"id": "1"}\n{"id": "2"}\n```'

    parsed = _parse_json(raw_text)

    assert parsed == [{"id": "1"}, {"id": "2"}]


def test_parse_json_strips_think_block_before_parsing_concatenated_objects():
    raw_text = '<think>reasoning...</think>{"id": "1"}\n{"id": "2"}'

    parsed = _parse_json(raw_text)

    assert parsed == [{"id": "1"}, {"id": "2"}]


def test_parse_json_raises_on_genuinely_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        _parse_json("not json at all")


async def test_qwen_provider_complete_raises_on_http_error(monkeypatch):
    class _FakeResponse:
        def raise_for_status(self):
            raise httpx.HTTPStatusError("boom", request=None, response=None)

        def json(self):
            return {}

    class _FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc_info):
            return False

        async def post(self, url, json):
            return _FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)

    provider = QwenProvider()

    try:
        await provider.complete("sys prompt", "user prompt")
        assert False, "expected HTTPStatusError to propagate"
    except httpx.HTTPStatusError:
        pass


def _sample_question(**overrides):
    from learn_with_masti.schemas import Question

    defaults = {
        "id": "addition_school_gen_1234",
        "topic": "addition",
        "track": "school",
        "difficulty": "easy",
        "question_text": "40 + 20 = ?",
        "options": ["58", "59", "60", "61"],
        "correct_answer": "60",
        "explanation_hint": "40 + 20 = 60.",
    }
    defaults.update(overrides)
    return Question.model_validate(defaults)


async def test_review_question_returns_approved_review(monkeypatch):
    async def fake_complete(system_prompt, user_prompt):
        return json.dumps({"approved": True, "problems": []})

    monkeypatch.setattr(
        llm_client, "get_review_provider", lambda: SimpleNamespace(complete=fake_complete)
    )

    review = await llm_client.review_question(_sample_question())

    assert review.approved is True
    assert review.problems == []


async def test_review_question_returns_rejected_review_with_problems(monkeypatch):
    async def fake_complete(system_prompt, user_prompt):
        return json.dumps(
            {"approved": False, "problems": ["distractors are not plausible"]}
        )

    monkeypatch.setattr(
        llm_client, "get_review_provider", lambda: SimpleNamespace(complete=fake_complete)
    )

    review = await llm_client.review_question(_sample_question())

    assert review.approved is False
    assert review.problems == ["distractors are not plausible"]


async def test_review_question_includes_question_details_in_prompt(monkeypatch):
    captured = {}

    async def fake_complete(system_prompt, user_prompt):
        captured["user_prompt"] = user_prompt
        return json.dumps({"approved": True, "problems": []})

    monkeypatch.setattr(
        llm_client, "get_review_provider", lambda: SimpleNamespace(complete=fake_complete)
    )

    await llm_client.review_question(_sample_question())

    assert "40 + 20 = ?" in captured["user_prompt"]
    assert "60" in captured["user_prompt"]
    assert "addition" in captured["user_prompt"]
    assert "school" in captured["user_prompt"]


async def test_review_question_raises_on_missing_required_field(monkeypatch):
    async def fake_complete(system_prompt, user_prompt):
        # "approved" is required by the QuestionReview schema.
        return json.dumps({"problems": []})

    monkeypatch.setattr(
        llm_client, "get_review_provider", lambda: SimpleNamespace(complete=fake_complete)
    )

    with pytest.raises(ValidationError):
        await llm_client.review_question(_sample_question())


async def test_review_question_raises_on_invalid_json(monkeypatch):
    async def fake_complete(system_prompt, user_prompt):
        return "not json at all"

    monkeypatch.setattr(
        llm_client, "get_review_provider", lambda: SimpleNamespace(complete=fake_complete)
    )

    with pytest.raises(json.JSONDecodeError):
        await llm_client.review_question(_sample_question())


def _question_json(**overrides) -> dict:
    defaults = {
        "id": "addition_school_gen_0001",
        "topic": "addition",
        "track": "school",
        "difficulty": "easy",
        "question_text": "40 + 20 = ?",
        "options": ["58", "59", "60", "61"],
        "correct_answer": "60",
        "explanation_hint": "40 + 20 = 60.",
    }
    defaults.update(overrides)
    return defaults


def _provider_returning(*payloads):
    """A fake Provider whose .complete() returns each payload in turn (as a
    JSON string), for stubbing successive generate_questions() attempts."""
    calls = iter(payloads)

    async def fake_complete(system_prompt, user_prompt):
        return json.dumps(next(calls))

    return SimpleNamespace(complete=fake_complete)


async def test_generate_questions_discards_stage1_failures(monkeypatch):
    good = _question_json(id="addition_school_gen_0001")
    bad = _question_json(id="addition_school_gen_0002", question_text="41 + 20 = ?")

    monkeypatch.setattr(llm_client, "get_provider", lambda: _provider_returning([good, bad]))
    monkeypatch.setattr(
        llm_client,
        "validate_question",
        lambda q: [] if q.id == "addition_school_gen_0001" else ["arithmetic is wrong"],
    )
    monkeypatch.setattr(llm_client, "REVIEW_ENABLED", False)

    result = await llm_client.generate_questions("addition", "school", "easy", 1, [])

    assert [q.id for q in result] == ["addition_school_gen_0001"]


async def test_generate_questions_discards_stage2_rejected_questions(monkeypatch):
    good = _question_json(id="addition_school_gen_0001")
    rejected = _question_json(id="addition_school_gen_0002", question_text="41 + 20 = ?")

    monkeypatch.setattr(llm_client, "get_provider", lambda: _provider_returning([good, rejected]))
    monkeypatch.setattr(llm_client, "validate_question", lambda q: [])
    monkeypatch.setattr(llm_client, "REVIEW_ENABLED", True)

    async def fake_review(question):
        from learn_with_masti.schemas import QuestionReview

        if question.id == "addition_school_gen_0001":
            return QuestionReview(approved=True, problems=[])
        return QuestionReview(approved=False, problems=["distractors are not plausible"])

    monkeypatch.setattr(llm_client, "review_question", fake_review)

    result = await llm_client.generate_questions("addition", "school", "easy", 1, [])

    assert [q.id for q in result] == ["addition_school_gen_0001"]


async def test_generate_questions_skips_review_when_disabled(monkeypatch):
    only = _question_json(id="addition_school_gen_0001")

    monkeypatch.setattr(llm_client, "get_provider", lambda: _provider_returning([only]))
    monkeypatch.setattr(llm_client, "validate_question", lambda q: [])
    monkeypatch.setattr(llm_client, "REVIEW_ENABLED", False)

    async def fail_review(question):
        raise AssertionError("review_question should not be called when REVIEW_ENABLED is False")

    monkeypatch.setattr(llm_client, "review_question", fail_review)

    result = await llm_client.generate_questions("addition", "school", "easy", 1, [])

    assert [q.id for q in result] == ["addition_school_gen_0001"]


async def test_generate_questions_retries_until_enough_survive(monkeypatch):
    rejected = _question_json(id="addition_school_gen_0001", question_text="41 + 20 = ?")
    good = _question_json(id="addition_school_gen_0002")

    monkeypatch.setattr(
        llm_client, "get_provider", lambda: _provider_returning([rejected], [good])
    )
    monkeypatch.setattr(llm_client, "validate_question", lambda q: [])
    monkeypatch.setattr(llm_client, "REVIEW_ENABLED", True)
    monkeypatch.setattr(llm_client, "LLM_MAX_ATTEMPTS", 2)

    async def fake_review(question):
        from learn_with_masti.schemas import QuestionReview

        approved = question.id == "addition_school_gen_0002"
        return QuestionReview(
            approved=approved, problems=[] if approved else ["not plausible"]
        )

    monkeypatch.setattr(llm_client, "review_question", fake_review)

    result = await llm_client.generate_questions("addition", "school", "easy", 1, [])

    assert [q.id for q in result] == ["addition_school_gen_0002"]


async def test_generate_questions_raises_when_nothing_survives_after_retries(monkeypatch):
    rejected1 = _question_json(id="addition_school_gen_0001")
    rejected2 = _question_json(id="addition_school_gen_0002")

    monkeypatch.setattr(
        llm_client, "get_provider", lambda: _provider_returning([rejected1], [rejected2])
    )
    monkeypatch.setattr(llm_client, "validate_question", lambda q: ["always fails"])
    monkeypatch.setattr(llm_client, "REVIEW_ENABLED", False)
    monkeypatch.setattr(llm_client, "LLM_MAX_ATTEMPTS", 2)

    with pytest.raises(ValueError, match="No generated questions passed"):
        await llm_client.generate_questions("addition", "school", "easy", 1, [])


async def test_generate_questions_logs_discarded_questions(monkeypatch, caplog):
    bad = _question_json(id="addition_school_gen_0001", question_text="41 + 20 = ?")
    good = _question_json(id="addition_school_gen_0002")

    monkeypatch.setattr(llm_client, "get_provider", lambda: _provider_returning([bad, good]))
    monkeypatch.setattr(
        llm_client,
        "validate_question",
        lambda q: [] if q.id == "addition_school_gen_0002" else ["arithmetic is wrong"],
    )
    monkeypatch.setattr(llm_client, "REVIEW_ENABLED", False)

    with caplog.at_level(logging.INFO, logger="learn_with_masti.llm_client"):
        await llm_client.generate_questions("addition", "school", "easy", 1, [])

    assert any(
        "addition_school_gen_0001" in record.message and "arithmetic is wrong" in record.message
        for record in caplog.records
    )
