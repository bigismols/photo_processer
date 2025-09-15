from flaskr import create_app, celery_init_app

flask_app = create_app()
celery = celery_init_app(flask_app)