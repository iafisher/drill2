import sqlite3
from dataclasses import dataclass
from typing import List, Optional

import click
from flask import current_app, g


@dataclass
class Question:
    question_id: int
    text: str
    answer: str
    strength: int
    time_last_asked: Optional[int]


@dataclass
class Answer:
    answer_id: int
    question: Question
    text: str
    grade: int


def create_question(db, text: str, answer: str) -> None:
    raise NotImplementedError


def list_questions(db) -> List[Question]:
    raise NotImplementedError


def create_answer(db, answer: str) -> None:
    raise NotImplementedError


def list_answers(db) -> List[Answer]:
    raise NotImplementedError


def fetch_answer(db, answer_id: int) -> Optional[Answer]:
    raise NotImplementedError


def get_db():
    if "db" not in g:
        # https://iafisher.com/blog/2021/10/using-sqlite-effectively-in-python
        g.db = sqlite3.connect(current_app.config["DATABASE"], isolation_level=None)
        g.db.execute("PRAGMA foreign_keys = 1")
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@click.command("init-db")
def init_db():
    db = get_db()
    with current_app.open_resource("sql/schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)
