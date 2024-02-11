DROP TABLE IF EXISTS answer;
DROP TABLE IF EXISTS question;

CREATE TABLE question
(
    question_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    text            TEXT NOT NULL,
    answer          TEXT NOT NULL,
    strength        INTEGER NOT NULL DEFAULT 0,
    -- seconds since the Unix epoch
    time_last_asked INTEGER DEFAULT NULL,
    time_created    INTEGER NOT NULL
);

CREATE TABLE answer
(
    answer_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id  INTEGER NOT NULL,
    text         TEXT NOT NULL,
    grade        INTEGER NOT NULL,
    -- seconds since the Unix epoch
    time_created INTEGER NOT NULL,

    FOREIGN KEY (question_id) REFERENCES question(question_id) ON DELETE SET NULL
);