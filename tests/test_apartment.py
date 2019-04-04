import pytest
import json
from flask import g, session
from groupnest.db import get_db


def test_index(client, auth, app):
    client.get('/')
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM apartment ORDER BY created DESC LIMIT 10')
        apartment = cursor.fetchall()    
        assert apartment is not None
        assert apartment[0]['room_number'] == 2
        assert apartment[1]['zip'] == 98107


def test_search(client, auth, app):
    response = client.get('/apartment/search')
    assert b'Redirecting' in response.data

    response = client.post('/apartment/search', data={'zip': '98105'})
    assert response.status_code == 404
    assert b'No such apartment matching given zipcode exists in our databse. Sorry! :(' in response.data

# TODO: May edit respson in apartment.py file then need to edit here
    response = client.post('/apartment/search', data={'zip': '98107'})
    assert b'"zip": 98107' in response.data

   # TODO: May edit here because orginally return a html
    response = client.get('/apartment/search', data={'zip': ''})
    assert b'Redirecting' in response.data


def test_delete_appartment(client, auth, app):
    auth.login()
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        assert client.post('/apartment/7/delete').status_code == 404
        response = client.post('/apartment/9/delete')
        assert b'doesn\'t exist.' in response.data
        client.post('/apartment/2/delete')
        cursor.execute('SELECT * FROM apartment WHERE apartment_id = 2')
        apartment = cursor.fetchone()
        assert apartment is None
        cursor.execute('SELECT * FROM nest WHERE nest_id = 2')
        nest = cursor.fetchall()
        assert len(nest) == 0
        cursor.execute(
            'SELECT * FROM reservation WHERE reservation_id = 2')
        reservation = cursor.fetchall()
        assert len(reservation) == 0


def test_update_appartment(client, auth, app):
    auth.login()

    response = client.get('/apartment/2/update')
    assert b'Are you sure?' in response.data

    assert client.get('/apartment/12/update').status_code == 403

    response = client.post('/apartment/2/update', data={'name': '', 'room_number': '2', 'bathroom_number':'2', 'zip':'98107', 'street_address':'HAHA', 'city':'Seattle', 'state':'WA', 'price':'1000','sqft':'200', 'description':'','photo_URL':''})
    assert b'Name is required.' in response.data

    response = client.post('/apartment/2/update', data={'name': 'AAA', 'room_number': '2', 'bathroom_number':'2', 'zip':'98107', 'street_address':'HAHA', 'city':'Seattle', 'state':'WA', 'price':'1000','sqft':'200', 'description':'','photo_URL':''})
    assert b'Redirecting' in response.data

    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM apartment WHERE apartment_id = 2')
        apartment = cursor.fetchone()
        assert apartment['name'] == 'AAA'


def test_create(client, auth, app):
    auth.login()
    assert client.get('/apartment/create').status_code == 200
    response = client.post('/apartment/create', data={'name': '',
                                                      'room_number': 5,
                                                      'bathroom_number': 5,
                                                      'street_address': '225 terry ave n', 'city': 'seattle', 'state': 'WA', 'zip': 98115,
                                                      'price': 250, 'sqft': 3500, 'description': 'big good', 'photo_URL': ''})
    assert response.status_code == 200
    assert b'name is required.' in response.data

    client.post('/create', data={'name': 'apartment1', 'room_number': 5, 'bathroom_number': 5,
                                 'street_address': '225 terry ave n', 'city': 'seattle', 'state': 'WA', 'zip': 98115,
                                 'price': 2500, 'sqft': 2500, 'description': 'big good'})
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM apartment WHERE apartment_id = 12')
        created = cursor.fetchone()
        assert created['zip'] == 98107


def test_browse(client, auth, app):
    auth.login()
    response = client.get('/apartment/12/browse')
    assert response.status_code == 200
    datas = json.loads(response.data)
    assert datas['room_number'] == 2
    assert datas['bathroom_number'] == 1
    assert datas['zip'] == 98107
    assert datas['street_address'] == 'HAHA'
    assert datas['city'] == 'Seattle'
    assert datas['state'] == 'WA'
    assert datas['name'] == 'apt2'
    assert datas['landlord_id'] == 12

    response = client.get('/apartment/42/browse')
    assert response.status_code == 404
    assert b"Apartment id 42 doesn't exist." in response.data


def test_get_ownerList(client, auth, app):
    auth.login()
    response = client.get('/apartment/ownerList')
    assert response.status_code == 200
    datas = json.loads(response.data)
    assert 2 == len(datas)


def test_get_reservationList(client, auth, app):
        auth.login()
        response = client.get('/apartment/reserveList')
        assert response.status_code == 200
        datas = json.loads(response.data)

        assert 8 == len(datas)
        assert datas[7]['accept_offer'] == 0
        assert datas[1]['nest_id'] == 22
