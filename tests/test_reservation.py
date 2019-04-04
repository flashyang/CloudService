import pytest
from groupnest.db import get_db

def test_login_required(client):
    response = client.post('reservation/create/nest_id/2')
    assert response.headers['Location'] == 'http://localhost/auth'

    response = client.put('reservation/2/accept_offer')
    assert response.headers['Location'] == 'http://localhost/auth'

    response = client.delete('reservation/2/delete')
    assert response.headers['Location'] == 'http://localhost/auth'

def test_author_required(app, client, auth):

    auth.login()
    # current user can't modify other user's reservation
    assert client.put('reservation/12/accept_offer').status_code == 403
    assert client.delete('reservation/12/delete').status_code == 403
    
def test_exists_required(client, auth):
    auth.login()
    assert client.put('reservation/20/update').status_code == 404
    assert client.delete('reservation/20/delete').status_code == 404

@pytest.mark.parametrize(('path', 'message'), (
    ('reservation/create/nest_id/62', b'You can only join five nests under one apartment.'),
    ('reservation/create/nest_id/72', b"Can't reserve, this nest is full."),
))
def test_create_validate(client, auth, path, message):
    auth.login()
    response = client.post(path, data={})
    assert message in response.data

def test_create(client, auth, app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(reservation_id) FROM reservation')
        prevCount = cursor.fetchone()['COUNT(reservation_id)']
        auth.login()
        client.post('reservation/create/nest_id/22', data={})
        cursor.execute('SELECT COUNT(reservation_id) FROM reservation')
        count = cursor.fetchone()['COUNT(reservation_id)']
        assert count == prevCount + 1

@pytest.mark.parametrize(('path', 'message'), (
    ('reservation/32/accept_offer', b"Can't accept offer without approval from landlord."),
))
def test_accept_offer_validate(client, auth, path, message):
    auth.login()
    response = client.put(path, data={})
    assert message in response.data

def test_accept_offer(client, auth, app):
    auth.login()
    client.put('reservation/2/accept_offer', data={})

    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM reservation WHERE reservation_id = 2')
        reservation = cursor.fetchone()
        assert reservation['accept_offer'] == 1
        cursor.execute('SELECT * FROM nest WHERE nest_id = 12')
        other_nest = cursor.fetchone()
        assert other_nest['status'] == 'REJECTED'

@pytest.mark.parametrize(('path', 'message'), (
    ('reservation/2/delete', b"You can't cancel a reservation once accept offer."),
))
def test_delete_validate(client, auth, path, message):
    auth.login()
    client.put('reservation/2/accept_offer')
    response = client.delete(path, data={})
    assert message in response.data

def test_delete(client, auth, app):
    auth.login()
    response = client.delete('reservation/2/delete')

    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM reservation WHERE reservation_id = 2')
        reservation = cursor.fetchone()
        assert reservation is None
        cursor.execute('SELECT * FROM nest WHERE nest_id = 2')
        nest = cursor.fetchone()
        assert nest['status'] == 'PENDING'

def test_delete_empty_nest(client, auth, app):
    auth.login()
    response = client.delete('reservation/32/delete')

    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM reservation WHERE reservation_id = 32')
        reservation = cursor.fetchone()
        assert reservation is None
        cursor.execute('SELECT * FROM nest WHERE nest_id = 22')
        nest = cursor.fetchone()
        assert nest is None
