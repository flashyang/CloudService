import pytest
from groupnest.db import get_db

def test_login_required(client):
    response = client.post('reservation/create/nest_id/1')
    assert response.headers['Location'] == 'http://localhost/auth/login'

    response = client.put('reservation/1/accept_offer')
    assert response.headers['Location'] == 'http://localhost/auth/login'

    response = client.delete('reservation/1/delete')
    assert response.headers['Location'] == 'http://localhost/auth/login'

def test_author_required(app, client, auth):

    auth.login()
    # current user can't modify other user's reservation
    assert client.put('reservation/2/accept_offer').status_code == 403
    assert client.delete('reservation/2/delete').status_code == 403
    
def test_exists_required(client, auth):
    auth.login()
    assert client.put('reservation/20/update').status_code == 404
    assert client.delete('reservation/20/delete').status_code == 404

@pytest.mark.parametrize(('path', 'message'), (
    ('reservation/create/nest_id/7', b'You can only join five nests under one apartment.'),
    ('reservation/create/nest_id/8', b"Can't reserve, this nest is full."),
))
def test_create_validate(client, auth, path, message):
    auth.login()
    response = client.post(path, data={})
    assert message in response.data

def test_create(client, auth, app):
    with app.app_context():
        db = get_db()
        prevCount = db.execute('SELECT COUNT(reservation_id) FROM reservation').fetchone()[0]
        auth.login()
        client.post('reservation/create/nest_id/3', data={})
        count = db.execute('SELECT COUNT(reservation_id) FROM reservation').fetchone()[0]
        assert count == prevCount + 1

@pytest.mark.parametrize(('path', 'message'), (
    ('reservation/4/accept_offer', b"Can't accept offer without approval from landlord."),
))
def test_accept_offer_validate(client, auth, path, message):
    auth.login()
    response = client.put(path, data={})
    assert message in response.data

def test_accept_offer(client, auth, app):
    auth.login()
    client.put('reservation/1/accept_offer', data={})

    with app.app_context():
        db = get_db()
        reservation = db.execute('SELECT * FROM reservation WHERE reservation_id = 1').fetchone()
        assert reservation['accept_offer'] == 1
        other_nest = db.execute('SELECT * FROM nest WHERE nest_id = 2').fetchone()
        assert other_nest['status'] == 'REJECTED'

@pytest.mark.parametrize(('path', 'message'), (
    ('reservation/1/delete', b"You can't cancel a reservation once accept offer."),
))
def test_delete_validate(client, auth, path, message):
    auth.login()
    client.put('reservation/1/accept_offer')
    response = client.delete(path, data={})
    assert message in response.data

def test_delete(client, auth, app):
    auth.login()
    response = client.delete('reservation/1/delete')

    with app.app_context():
        db = get_db()
        reservation = db.execute('SELECT * FROM reservation WHERE reservation_id = 1').fetchone()
        assert reservation is None
        nest = db.execute('SELECT * FROM nest WHERE nest_id = 1').fetchone()
        assert nest['status'] == 'PENDING'

def test_delete_empty_nest(client, auth, app):
    auth.login()
    response = client.delete('reservation/4/delete')

    with app.app_context():
        db = get_db()
        reservation = db.execute('SELECT * FROM reservation WHERE reservation_id = 4').fetchone()
        assert reservation is None
        nest = db.execute('SELECT * FROM nest WHERE nest_id = 3').fetchone()
        assert nest is None