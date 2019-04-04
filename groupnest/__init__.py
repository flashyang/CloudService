import os
import urllib

from flask import Flask
import urllib


def create_app(test_config=None):

    from logging.config import dictConfig
    # create a logging configuration
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'groupnest.sqlite'),
    )
    url = urllib.parse.urlparse(os.environ['DATABASE_URL'])
    app.config["DATABASE_HOSTNAME"] = url.hostname
    app.config["DATABASE_USERNAME"] = url.username
    app.config["DATABASE_PASSWORD"] = url.password
    app.config["DATABASE_NAME"]     = url.path[1:]

    url = urllib.parse.urlparse(os.environ['DATABASE_URL'])
    app.config["DATABASE_HOSTNAME"] = url.hostname
    app.config["DATABASE_USERNAME"] = url.username
    app.config["DATABASE_PASSWORD"] = url.password
    app.config["DATABASE_NAME"]     = url.path[1:]
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import apartment
    app.register_blueprint(apartment.bp)
    app.add_url_rule('/', endpoint='index', view_func=apartment.index)

    from . import nest
    app.register_blueprint(nest.bp)

    from . import reservation
    app.register_blueprint(reservation.bp)

    return app