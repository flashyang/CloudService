import os
import tempfile
import urllib

import pytest
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

    app.config["DATABASE_HOSTNAME"] = "localhost"
    app.config["DATABASE_USERNAME"] = "root"
    app.config["DATABASE_PASSWORD"] = ""
    app.config["DATABASE_NAME"]     = "groupnestdatabase"

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

    def login(self, username='test', password='test', first_name='first', last_name='last', email='test@gmail.com', gender='FEMALE', description='good'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password, 'first_name': first_name,
                  'last_name': last_name, 'email': email, 'gender': gender, 'description': description}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
