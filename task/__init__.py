import os

from flask import Flask


def create_app():

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "task.sqlite"),
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    
    from task import db
    db.init_app(app)

    
    from task import auth, blog
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    app.add_url_rule("/", endpoint="index")

    return app
