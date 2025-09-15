import os
from celery import Celery, Task
from flask import Flask

celery_app = Celery(__name__)

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        CELERY=dict(
            broker_url="amqp://guest:guest@localhost:5672//",
            result_backend="rpc://",
            task_ignore_result=False,
        ),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    celery_init_app(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    with app.app_context():
        if not os.path.exists(app.config["DATABASE"]):
            db.init_db()

    from .routes import images_bp, stats_bp
    app.register_blueprint(images_bp)
    app.register_blueprint(stats_bp)

    return app