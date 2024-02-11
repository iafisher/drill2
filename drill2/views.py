from flask import (
    Blueprint,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from . import repetition, storage

bp = Blueprint("views", __name__)


@bp.route("/", methods=("GET", "POST"))
def home_page():
    db = storage.get_db()
    if request.method == "GET":
        messages = get_flashed_messages()
        questions = storage.list_questions(db)
        question = repetition.select_question(questions)
        return render_template(
            "ask_question.html", messages=messages, question=question
        )
    else:
        question_id = int(request.form["question_id"])
        answer = request.form["answer"].strip()
        question = storage.fetch_question(db, question_id)
        return render_template("grading.html", question=question, answer=answer)


@bp.route("/submit/grade", methods=("POST",))
def submit_grade():
    db = storage.get_db()
    question_id = int(request.form["question_id"])
    answer = request.form["answer"].strip()
    grade = int(request.form["grade"])
    storage.create_answer(db, question_id, answer, grade)
    flash("Answer submitted")
    return redirect(url_for("views.home_page"))


@bp.route("/new-question", methods=("GET", "POST"))
def new_question_page():
    if request.method == "GET":
        return render_template("new_question.html")
    else:
        db = storage.get_db()
        text = request.form["text"].strip()
        answer = request.form["answer"].strip()
        storage.create_question(db, text, answer)
        flash("Created question")
        return redirect(url_for("views.home_page"))
