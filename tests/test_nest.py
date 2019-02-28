import pytest
from flask import g, session
from groupnest.db import get_db


# def test_index(client, auth):
#     response = client.get('/')
#     assert b"Log In" in response.data
#     assert b"Register" in response.data

#     auth.login()
#     response = client.get('/')
#     assert b'Log Out' in response.data
#     assert b'test title' in response.data
#     assert b'by test on 2018-01-01' in response.data
#     assert b'test\nbody' in response.data
#     assert b'href="/1/update"' in response.data


# @pytest.mark.parametrize('path', (
#     '/create',
#     '/1/update',
#     '/1/delete',
# ))
# def test_login_required(client, path):
#     response = client.post(path)
#     assert response.headers['Location'] == 'http://localhost/auth/login'


# def test_author_required(app, client, auth):
#     # change the post author to another user
#     with app.app_context():
#         db = get_db()
#         db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
#         db.commit()

#     auth.login()
#     # current user can't modify other user's post
#     assert client.post('/1/update').status_code == 403
#     assert client.post('/1/delete').status_code == 403
#     # current user doesn't see edit link
#     assert b'href="/1/update"' not in client.get('/').data


# @pytest.mark.parametrize('path', (
#     '/2/update',
#     '/2/delete',
# ))
# def test_exists_required(client, auth, path):
#     auth.login()
#     assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    response = client.get('/nest/11/create')
    assert response.status_code == 404
    assert b'Apartment not found.' in response.data

    assert client.get('/nest/1/create').status_code == 200

    for i in range(5):
        response = client.post('/nest/2/create')
        with app.app_context():
            db = get_db()
            record = db.execute(
                'SELECT DISTINCT n.nest_id'
                ' FROM nest n JOIN reservation r ON n.nest_id = r.nest_id'
                ' WHERE r.tenant_id = ?'
                ' AND n.apartment_id = ?'
                ' ORDER BY created DESC',
                (g.user['user_id'], 2)
            ).fetchall()

        if i < 4:
            assert response.status_code == 200
            assert b'save successfully' in response.data
            assert len(record) == 2+i
        else:
            assert response.status_code == 403
            assert b'User has already been added to five nests belong to this apartment. Please cancal the previous reservation and create a new nest again.' in response.data
            assert len(record) == 5

    # clean up
    for i in range(5):
        with app.app_context():
            db = get_db()
            db.execute(
                'DELETE'
                ' FROM reservation'
                ' WHERE nest_id = ?'
                (4+i,)
            )
            db.commit()
            db.execute(
                'DELETE'
                ' FROM nest'
                ' WHERE nest_id = ?'
                (4+i,)
            )
            db.commit()


def test_update(client, auth, app):
    auth.login()
    response = client.get('/nest/11/update')
    assert response.status_code == 404
    assert b'Nest not found' in response.data

    assert client.get('/nest/1/update').status_code == 200

    response = client.post('/nest/1/update', data={'decision': ''})
    assert b'Decision is required.' in response.data

    response = client.post('/nest/1/update', data={'decision': 'APPROVED'})
    assert response.status_code == 200
    assert b'updated nest status' in response.data
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
    response = client.post('/nest/2/update', data={'decision': 'APPROVED'})
    assert b'This nest is not full yet, landlord cannot alter nest status' in response.data


# @pytest.mark.parametrize('path', (
#     '/create',
#     '/1/update',
# ))
# def test_create_update_validate(client, auth, path):
#     auth.login()
#     response = client.post(path, data={'title': '', 'body': ''})
#     assert b'Title is required.' in response.data


# def test_delete(client, auth, app):
#     auth.login()
#     response = client.post('/1/delete')
#     assert response.headers['Location'] == 'http://localhost/'

#     with app.app_context():
#         db = get_db()
#         post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
#         assert post is None
