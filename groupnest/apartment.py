from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from groupnest.auth import login_required
from groupnest.db import get_db

bp = Blueprint('apartment', __name__, url_prefix='/apartment')


#GET: / Return the index page
@bp.route('/')
def index():
    db = get_db()
    aprtments = db.execute(
        'SELECT top(10)*'
        'FROM db'
        'ORDER BY created DESC'
    ).fetchall()

#GET: /apartment/<int: zipcode>/search (zipcode)
#Get a list of apartments by searching zipcode
@bp.route('/<int:id>/search', methods=('GET',))
def search(zipcode):
    db = get_db()
    aprtments = db.execute(
        'SELECT *'
        'FROM db'
        'ORDER BY created DESC'
        'WHERE zip = ?',
        (zipcode,)
    ).fetchall()
    if aprtments is None:
        abort(Response("No such zipcode exists in our databse. Sorry! :("))
    return aprtments
