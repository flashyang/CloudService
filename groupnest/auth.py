import functools
import logging

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from groupnest.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        gender = request.form['gender'].upper()
        description = request.form['description']

        db = get_db()
        cursor = db.cursor()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else:
            cursor.execute('SELECT user_id FROM user WHERE username= %s', (username,))
            if cursor.fetchone() is not None:
                error = 'User {} is already registered.'.format(username)

        if error is None:
            try:
                cursor.execute(
                    'INSERT INTO user (username, password, first_name, last_name, email, gender, description) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (username, generate_password_hash(password),
                        first_name, last_name, email, gender, description)
                )
                db.commit()
                logging.info('One user registered!')
                return redirect(url_for('auth.login'))
            except Exception as e:
                print(e)
                error = 'Gender should be male, female or other.'

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        error = None
        cursor.execute(
            'SELECT * FROM user WHERE username = %s', (username,)
        )
        user = cursor.fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['user_id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('apartment.index'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    cursor = get_db().cursor()

    if user_id is None:
        g.user = None
    else:
        cursor.execute(
            'SELECT * FROM user WHERE user_id = %s', (user_id,)
        )
        g.user = cursor.fetchone()
    print(user_id)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
