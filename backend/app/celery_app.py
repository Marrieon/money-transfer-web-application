from . import create_app
from celery import Celery

def make_celery(app):
    """
    Configures and returns a Celery object that is integrated with the Flask app context.
    """
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# We create a dummy Flask app here just to get the config for Celery.
# The 'create_app' function will be called properly by our workers.
flask_app = create_app()
celery = make_celery(flask_app)