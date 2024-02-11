import contextlib
import os

from flask import Flask, render_template


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "drill2.sqlite3")
    )

    with contextlib.suppress(OSError):
        os.makedirs(app.instance_path)

    @app.route("/")
    def home_page():
        return render_template("grading.html")

    from . import db
    db.init_app(app)

    return app
