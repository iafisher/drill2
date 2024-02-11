import contextlib
import os
import sqlite3
import sys
import time
from dataclasses import dataclass
from typing import List, Optional

import click
from flask import Flask, current_app, g


@dataclass
class Question:
    question_id: int
    text: str
    answer: str
    strength: int
    time_last_asked: Optional[int]

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Question":
        return cls(
            question_id=row["question.question_id"],
            text=row["question.text"],
            answer=row["question.answer"],
            strength=row["question.strength"],
            time_last_asked=row["question.time_last_asked"],
        )


QUESTION_SELECT_FIELDS = "question.question_id, question.text, question.answer, question.strength, question.time_last_asked"


@dataclass
class Answer:
    answer_id: int
    question: Question
    text: str
    grade: int

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Answer":
        return cls(
            answer_id=row["answer.answer_id"],
            question=Question.from_row(row),
            text=row["answer.text"],
            grade=row["answer.grade"],
        )


ANSWER_SELECT_FIELDS = "answer.answer_id, answer.text, answer.grade"


def create_question(db: sqlite3.Connection, text: str, answer: str) -> None:
    time_created = int(time.time())
    db.execute(
        """
        INSERT INTO question(text, answer, time_created)
        VALUES (:text, :answer, :time_created)
        """,
        dict(text=text, answer=answer, time_created=time_created),
    )


def list_questions(db: sqlite3.Connection) -> List[Question]:
    rows = db.execute(
        f"""
        SELECT {QUESTION_SELECT_FIELDS} FROM question
        """
    ).fetchall()
    return [Question.from_row(row) for row in rows]


def create_answer(
    db: sqlite3.Connection, question_id: int, text: str, grade: int
) -> None:
    current_time = int(time.time())
    with _tx(db) as dbtx:
        dbtx.execute(
            """
            INSERT INTO answer(question_id, text, grade, time_created)
            VALUES (:question_id, :text, :grade, :time_created)
            """,
            dict(
                question_id=question_id,
                text=text,
                grade=grade,
                time_created=current_time,
            ),
        )
        dbtx.execute(
            """
            UPDATE question SET time_last_asked = :time_last_asked WHERE question_id = :question_id
            """,
            dict(question_id=question_id, time_last_asked=current_time),
        )


def list_answers(db: sqlite3.Connection) -> List[Answer]:
    rows = db.execute(
        f"""
        SELECT {QUESTION_SELECT_FIELDS}, {ANSWER_SELECT_FIELDS}
        FROM answer
        JOIN question
        ON answer.question_id = question.question_id
        """
    ).fetchall()
    return [Answer.from_row(row) for row in rows]


def fetch_question(db: sqlite3.Connection, question_id: int) -> Optional[Question]:
    row_or_none = db.execute(
        f"""
        SELECT {QUESTION_SELECT_FIELDS}
        FROM question
        WHERE question_id = :question_id
        """,
        dict(question_id=question_id),
    ).fetchone()
    return Question.from_row(row_or_none) if row_or_none is not None else None


def fetch_answer(db: sqlite3.Connection, answer_id: int) -> Optional[Answer]:
    row_or_none = db.execute(
        f"""
        SELECT {QUESTION_SELECT_FIELDS}, {ANSWER_SELECT_FIELDS}
        FROM answer
        JOIN question
        ON answer.question_id = question.question_id
        WHERE answer_id = :answer_id
        """,
        dict(answer_id=answer_id),
    ).fetchone()
    return Answer.from_row(row_or_none) if row_or_none is not None else row_or_none


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        # https://iafisher.com/blog/2021/10/using-sqlite-effectively-in-python
        g.db = sqlite3.connect(current_app.config["DATABASE"], isolation_level=None)
        g.db.execute("PRAGMA foreign_keys = ON")
        # https://github.com/python/cpython/issues/49355
        g.db.execute("PRAGMA full_column_names = ON")
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


@click.command("init-db")
def init_db_cmd() -> None:
    if os.path.exists(current_app.config["DATABASE"]):
        _confirm("Database already exists. Do you want to overwrite it?")

    db = get_db()
    with current_app.open_resource("sql/schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))


@click.command("clear-answers")
def clear_answers_cmd() -> None:
    db = get_db()
    count = len(list_answers(db))
    _confirm(f"Delete 'answer' table of size {count}?")
    db.execute("DELETE FROM answer")


def _confirm(prompt: str) -> None:
    if not click.confirm(prompt):
        click.echo("Aborting.", err=True)
        sys.exit(2)


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_cmd)
    app.cli.add_command(clear_answers_cmd)


@contextlib.contextmanager
def _tx(db: sqlite3.Connection):
    try:
        db.execute("BEGIN TRANSACTION")
        yield db
    except:
        db.execute("ROLLBACK")
    else:
        db.execute("COMMIT")
