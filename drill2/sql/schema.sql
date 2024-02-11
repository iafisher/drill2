CREATE TABLE IF NOT EXISTS question
(
    question_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    text            TEXT NOT NULL,
    answer          TEXT NOT NULL,
    strength        INTEGER NOT NULL,
    -- seconds since the Unix epoch
    time_last_asked INTEGER,
    time_created    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS answer
(
    answer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER,
    text        TEXT NOT NULL,
    grade       INTEGER NOT NULL,
    -- seconds since the Unix epoch
    created_at  INTEGER NOT NULL,

    FOREIGN KEY (question_id) REFERENCES question(question_id) ON DELETE SET NULL
);