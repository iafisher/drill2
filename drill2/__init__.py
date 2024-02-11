import contextlib
import os

from flask import Flask, render_template


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE=os.path.join(app.instance_path, "drill2.sqlite3")
    )

    # ensure instance directory exists
    with contextlib.suppress(OSError):
        os.makedirs(app.instance_path)

    from . import storage

    storage.init_app(app)

    from . import views

    app.register_blueprint(views.bp)

    return app
