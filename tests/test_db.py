from learn_with_masti.db import _build_connect_args


def test_postgres_connect_args_bound_connect_and_statement_timeout():
    args = _build_connect_args("postgresql+psycopg://masti:masti@localhost:5433/learn_with_masti")

    assert args["connect_timeout"] > 0
    assert "statement_timeout" in args["options"]


def test_sqlite_connect_args_are_unaffected():
    assert _build_connect_args("sqlite:///local.db") == {}
