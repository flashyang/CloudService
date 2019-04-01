import functools
import logging
from flask import (
    Flask,Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response, jsonify
)
from groupnest.db import get_db
from flask_oauth import OAuth
from requests_oauthlib import OAuth2Session
from urllib.request import Request, urlopen, URLError
import requests
from groupnest.db import get_db

bp = Blueprint('auth', __name__)



GOOGLE_CLIENT_ID = '569147715346-hj17stsvc1m93e4nj3jjo5qt1g6csv21.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'k90emyx-vSVBe_uMy6FICkwu'
REDIRECT_URI = '/apartment'  # one of the Redirect URIs from Google APIs console

SECRET_KEY = 'development key'
DEBUG = True
bp = Blueprint('auth', __name__)
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)

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

@bp.route('/auth')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('auth.login'))

    access_token = access_token[0]

    headers = {'Authorization': 'Bearer ' +access_token}
                            
    req = requests.get('https://www.googleapis.com/oauth2/v1/userinfo',
                  headers = headers)
    if not req.status_code is 200:
        #Bad token, need to re-login
        session.pop('access_token', None)
        return redirect(url_for('auth.login'))
    username = req.json()['email']
    first_name = req.json()['given_name']
    last_name = req.json()['family_name']
    email = req.json()['email']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM user WHERE username= %s', (email,))
    user = cursor.fetchone()
    # store the user id in a new session and return to the index
    session.clear()
    # session['user_id'] = user['user_id']
    if user is None:
        cursor.execute(
            'INSERT INTO user (username, first_name, last_name, email)'
            ' VALUES(%s, %s, %s,%s)',
            (username, first_name, last_name, email)
        )
        db.commit()
        cursor.execute('SELECT * FROM user WHERE username= %s', (email,))
        user = cursor.fetchone()
        logging.info('One user registered!')
    session['user_id'] = user['user_id']
    return redirect(url_for('apartment.index'))



@bp.route('/auth/login')
def login():
    callback=url_for('auth.authorized', _external=True)
    return google.authorize(callback=callback)



@bp.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('auth.index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')

@bp.route('/auth/logout')
def logout():
    session.clear()
    return redirect(url_for('apartment.index'))

# if __name__ == '__main__':
#    app.run()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            print("No user")
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view



