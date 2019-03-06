import pytest
import json
from flask import g, session
from groupnest.db import get_db


def test_index(client, auth, app):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data
    auth.login()
    response = client.get('/')
    with app.app_context():
        db = get_db()
        apartment = db.execute(
            'SELECT * FROM apartment ORDER BY created DESC LIMIT 10').fetchall()
        assert apartment is not None

def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    response = client.post('/create', data={'name': 'apartment1',
                                            #'room_number': 5,
                                            'bathroom_number':5,
                                 'street_address':'225 terry ave n', 'city':'seattle', 'state':'WA', 'zip':98115,
                                 'price': 250, 'sqft':3500, 'description':'big good'})
    assert response.status_code == 403
    assert b'room_number is required.' in response.data


    client.post('/create', data={'name': 'apartment1', 'room_number': 5, 'bathroom_number':5,
                                 'street_address':'225 terry ave n', 'city':'seattle', 'state':'WA', 'zip':98115,
                                 'price': 2500, 'sqft':2500, 'description':'big good'})
    with app.app_context():
        db = get_db()
        created = db.execute('SELECT * FROM post WHERE apartment_id = 4').fetchone()
        assert created['price'] == 2500

def test_browse(client, auth, app):
    assert client.get('/1/browse').status_code == 200

    response = client.get('/1/browse')
    assert response.data == {'name': 'apt1', 'room_number': 2, 'bathroom_number':2,
                                 'street_address':'HAHA', 'city':'Seattle', 'state':'WA', 'zip':98107,
                                 'price': 2500, 'sqft':2500, 'description':'', 'photo_URL':'','apartment_id':1}

    response = client.get('/5/browse')
    assert response.status_code == 404
    assert b"Apartment id 5 doesn't exist." in response.data

def test_get_ownerList(client, auth, app):
    with app.app_context():
        db = get_db()
        db.execute('UPDATE user SET user_id = 2')
        db.commit()

    auth.login()
    assert client.get('/ownerList').status_code == 200

    response = client.get('/ownerList')
    assert response.data == {'name': 'apt2', 'room_number': 2, 'bathroom_number':1,
                                 'street_address':'HAHA', 'city':'Seattle', 'state':'WA', 'zip':98107,
                                 'price': 2500, 'sqft':2500, 'description':'', 'photo_URL':'','description':''}

    with app.app_context():
        db = get_db()
        db.execute('UPDATE user SET user_id = 3')
        db.commit()

    response = client.get('/ownerList')

    auth.login()
    assert response.status_code == 404
    assert b"There is no apartments in your account:(" in response.data

def test_search(client, auth, app):
    response = client.post('/search', data={'zip': ' '})
    assert b'ZipCode is required.' in response.data

    response = client.post('/search', data={'zip': '98105'})
    assert response.status_code == 404
    assert b'No such apartment matching given zipcode exists in our databse. Sorry! :(' in response.data

# TODO: May edit respson in apartment.py file then need to edit here
    response = client.post('/search', data={'zip': '98107'})
    assert b'Searching result is in construction' in response.data

   # TODO: May edit here because orginally return a html
    response = client.get('/search', data={'zip': ''})
    assert b'Redirecting' in response.data


def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_author_required(app, client, auth):

    auth.login()
    # current user can't modify other user's reservation
    assert client.post('/2/delete').status_code == 403
    assert client.post('/2/update').status_code == 403
    assert client.get('/').status_code == 403


def test_delete_appartment(client, auth, app):
    auth.login()
    client.post('/1/delete')
    with app.app_context():
        db = get_db()
        apartment = db.execute(
            'SELECT * FROM apartment WHERE id = 1').fetchone()
        assert apartment is None
        nest = db.execute('SELECT * FROM nest WHERE nest_id = 1').fetchall()
        assert len(nest) == 0
        reservation = db.execute(
            'SELECT * FROM reservation WHERE reservation_id = 1').fetchall()
        assert len(reservation) == 0


def test_update_appartment(client, auth, app):
    auth.login()

    response = client.get('/apartment/1/update')
    assert b'Redirecting' in response.data

    response = client.post('/apartment/1/update', data={'name': ''})
    assert b'Name is required.' in response.data

    response = client.post('/apartment/1/update', data={'name': 'AAA'})
    assert b'Redirecting' in response.data
    #assert b'updated nest status' in response.data
    with app.app_context():
        db = get_db()
        apartment = db.execute(
            'SELECT * FROM apartment WHERE id = 1').fetchone()
        assert apartment['name'] == 'AAA'
