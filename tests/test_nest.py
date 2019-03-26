import pytest
import json
import logging
from flask import g, session
from groupnest.db import get_db

def test_get_fullNest(client, auth, app):
    auth.login()
    response = client.get('/nest/1/fullNest')
    datas = json.loads(response.data)
    assert 2 == len(datas)

def test_get_notfullNest(client, auth, app):
    auth.login()
    response = client.get('/nest/1/notFullNest')
    datas = json.loads(response.data)
    assert 4 == len(datas)

def test_get_allNests(client, auth, app):
    auth.login()
    response = client.get('/nest/1/allNests')
    data = json.loads(response.data)
    full_nest = data['fullnest']
    not_full = data['notFullnest']
    assert 6 == len(full_nest) + len(not_full)

def test_nestUser(client, auth, app):
    auth.login()
    response = client.get('/nest/1')
    data = json.loads(response.data)
    assert 2 == data['room_number']
    assert 2 == data['user_number']
    assert 2 == len(data['user_list'])
    assert 'test' == data['user_list'][0]['username']
    assert 'other' == data['user_list'][1]['username']

def test_get_reserveNest(client, auth, app):
    auth.login()
    response = client.get('/nest/reserveNest')
    datas = json.loads(response.data)
    assert 8 == len(datas)
    apt1_count = 0
    apt2_count = 0
    apt3_count = 0
    for data in datas:
        if data['apartment_name'] == 'apt1':
            apt1_count += 1
        if data['apartment_name'] == 'apt2':
            apt2_count += 1
        if data['apartment_name'] == 'apt3':
            apt3_count + 1
    
    assert apt1_count == 0
    assert apt2_count == 1
    assert apt3_count == 0


def test_get_ownerNest(client, auth, app):
    auth.login()
    response = client.get('/nest/ownerNest')
    data = json.loads(response.data)
    assert 2 == len(data)
    assert 2 == len(data[0]['fullnest'])
    assert 4 == len(data[0]['notFullnest'])
    assert '11' == data[0]['apartment_name']
    assert 1 == len(data[1]['fullnest'])
    assert 0 == len(data[1]['notFullnest'])
    assert 'apt3' == data[1]['apartment_name']


def test_create(client, auth, app):

    auth.login()
    response = client.get('/nest/11/create')
    assert response.status_code == 404
    assert b'Apartment not found.' in response.data

    assert client.get('/nest/1/create').status_code == 200

    for i in range(5):
        response = client.post('/nest/2/create', data={})
        with app.app_context(), client:
            db = get_db()
            client.get('/')
            record = db.execute(
                'SELECT DISTINCT n.nest_id'
                ' FROM nest n JOIN reservation r ON n.nest_id = r.nest_id'
                ' WHERE r.tenant_id = ?'
                ' AND n.apartment_id = ?'
                ' ORDER BY created DESC',
                (g.user['user_id'], 2)
            ).fetchall()
            len(record) == 2+i

        if i < 4:
            assert b'Redirecting' in response.data
            assert len(record) == 2+i
        else:
            assert b'User has already been added to five nests belong to this apartment. Please cancal the previous reservation and create a new nest again.' in response.data
            assert len(record) == 5


def test_update(client, auth, app):
    auth.login()
    response = client.get('/nest/11/update')
    assert response.status_code == 404
    assert b'Nest not found' in response.data

    response = client.get('/nest/1/update')
    assert b'Redirecting' in response.data

    response = client.post('/nest/1/update', data={'decision': ''})
    assert b'Decision is required.' in response.data

    response = client.post('/nest/8/update', data={'decision': 'APPROVED'})
    assert response.status_code == 302
    assert b'Redirecting' in response.data
    with app.app_context():
        db = get_db()
        nest = db.execute(
            'SELECT status FROM nest WHERE nest_id = 1').fetchone()
        assert nest['status'] == 'APPROVED'

    response = client.post('/nest/1/update', data={'decision': 'REJECTED'})
    assert b'Cannot change nest status that is not PENDING' in response.data

    response = client.post('/nest/3/update', data={'decision': 'REJECTED'})
    assert b'Current user is not authorized to alter the status of this nest.' in response.data

    response = client.post('/nest/2/update', data={'decision': 'APPROVED'})
    assert b'Landlord has already approved one nest' in response.data

    with app.app_context():
        db = get_db()
        db.execute(
            'UPDATE nest SET status = ?'
            ' WHERE nest_id = ?',
            ('PENDING', 1)
        )
        db.commit()
    response = client.post('/nest/4/update', data={'decision': 'APPROVED'})
    assert b'This nest is not full yet, landlord cannot alter nest status' in response.data
