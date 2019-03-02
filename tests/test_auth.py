# import pytest
# from flask import g, session
# from groupnest.db import get_db


# def test_register(client, app):
#     assert client.get('/auth/register').status_code == 200
#     response = client.post(
#         '/auth/register', data={'username': 'test', 'password': 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f', 'first_name': 'first', 'last_name': 'last', 'email': 'test@gmail.com', 'gender': 'FEMALE', 'description': 'good'}
#     )

#     assert 'http://localhost/auth/login' == response.headers['Location']

#     with app.app_context():
#         assert get_db().execute(
#             "select * from user where username = 'a'",
#         ).fetchone() is not None


# @pytest.mark.parametrize(('username', 'password', 'first_name', 'last_name', 'email', 'gender', 'description', 'message'), (
#     ('', '', 'first', 'last', 'test@gmail.com',
#      'FEMALE', 'good', b'Username is required.'),
#     ('a', '', 'first', 'last', 'test@gmail.com',
#      'FEMALE', 'good', b'Password is required.'),
#     ('test', 'test', 'first', 'last', 'test@gmail.com',
#      'FEMALE', 'good', b'already registered'),
# ))
# def test_register_validate_input(client, username, first_name, last_name, email, gender, description, password, message):
#     response = client.post(
#         '/auth/register',
#         data={'username': username, 'password': password, 'first_name': first_name,
#               'last_name': last_name, 'email': email, 'gender': gender, 'description': description}
#     )
#     assert message in response.data


# def test_login(client, auth):
#     assert client.get('/auth/login').status_code == 200
#     response = auth.login()

#     assert response.headers['Location'] == 'http://localhost/'

#     with client:
#         client.get('/')
#         assert session['user_id'] == 1
#         assert g.user['username'] == 'test'


# @pytest.mark.parametrize(('username', 'password', 'message'), (
#     ('a', 'test', b'Incorrect username.'),
#     ('test', 'a', b'Incorrect password.'),
# ))
# def test_login_validate_input(auth, username, password, message):
#     response = auth.login(username, password)
#     assert message in response.data


# def test_logout(client, auth):
#     auth.login()

#     with client:
#         auth.logout()
#         assert 'user_id' not in session
