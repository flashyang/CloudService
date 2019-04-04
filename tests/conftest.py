import os
import tempfile
import urllib

import pytest
from flask import g, session
from groupnest import create_app
from groupnest.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')



@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        # 'DATABASE': db_path,
    })

    
    url = urllib.parse.urlparse(os.environ['TEST_DATABASE_URL'])
    app.config["DATABASE_HOSTNAME"] = url.hostname
    app.config["DATABASE_USERNAME"] = url.username
    app.config["DATABASE_PASSWORD"] = url.password
    app.config["DATABASE_NAME"]     = url.path[1:]

    with app.app_context():
        init_db()
        db = get_db()
        # get_db().executescript(_data_sql)

        ret = _data_sql.split(';')
        # drop last empty entry
        ret.pop()

        for stmt in ret:
            db.cursor().execute(stmt + ";")
        db.commit()

    yield app

    # os.close(db_fd)
    # os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(username='test', first_name='first', last_name='last', email='test@gmail.com'):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT user_id'
            ' FROM user'
            ' WHERE username = %s',
            (username,)
        )
        session.clear()
        userID = cursor.fetchone()['user_id']
        session['user_id'] = user['user_id']
        return true

    def logout(self):
        session.clear()
        return false


@pytest.fixture
def auth(client):
    return AuthActions(client)
