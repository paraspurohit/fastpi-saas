import pytest
from sqlalchemy import text

from app.database.db import get_db


def test_db_connection(db_session):
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_db_commit(db_session):
    db_session.execute(text("CREATE TABLE temp_table (id INT)"))
    db_session.commit()

    result = db_session.execute(
        text("SELECT table_name FROM information_schema.tables WHERE table_name='temp_table'")
    )
    assert result.fetchone() is not None


def test_db_rollback(db_session):
    db_session.execute(text("CREATE TABLE rollback_table (id INT)"))
    # no commit → fixture rollback should remove table


def test_db_rollback_effect(engine):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_name='rollback_table'")
        )
        assert result.fetchone() is None


def test_multiple_sessions_isolation(engine):
    conn1 = engine.connect()
    trans1 = conn1.begin()

    conn2 = engine.connect()

    conn1.execute(text("CREATE TABLE isolation_test (id INT)"))

    result = conn2.execute(
        text("SELECT table_name FROM information_schema.tables WHERE table_name='isolation_test'")
    )

    assert result.fetchone() is None

    trans1.rollback()
    conn1.close()
    conn2.close()

def test_get_db_multiple_calls(monkeypatch):
    calls = []

    class DummySession:
        def close(self):
            calls.append("closed")

    monkeypatch.setattr("app.database.db.SessionLocal", lambda: DummySession())

    for _ in range(3):
        gen = get_db()
        next(gen)
        try:
            next(gen)
        except StopIteration:
            pass

    assert len(calls) == 3


