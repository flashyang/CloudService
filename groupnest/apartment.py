from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from groupnest.auth import login_required
from groupnest.db import get_db

bp = Blueprint('apartment', __name__, url_prefix='/apartment')


# GET: / Return the index page
@bp.route('/')
def index():
    db = get_db()
    apartments = db.execute(
        'SELECT top(10)*'
        'FROM db'
        'ORDER BY created DESC'
    ).fetchall()

# GET: /apartment/<int: zipcode>/search (zipcode)
# Get a list of apartments by searching zipcode
@bp.route('/<int:zipcode>/search', methods=('GET',))
def search(zipcode):
    db = get_db()
    apartments = db.execute(
        'SELECT *'
        'FROM apartment'
        'ORDER BY created DESC'
        'WHERE zip = ?',
        (zipcode,)
    ).fetchall()
    if apartments is None:
        abort(
            "No such apartment matching given zipcode exists in our databse. Sorry! :(")
    return apartments

# Get a apartment by apartmentId


def get_apartment(apartmentId):
    aprtment = get_db().execute(
        'SELECT *'
        'FROM apartment'
        'WHERE apartment_id = ?',
        (apartmentId,)
    ).fetchone()

    if aprtment is None:
        abort(404, "Apartment id {0} doesn't exist.".format(apartmentId))

    return aprtment

# DELETE: /apartment/<int: apartmentId>/delete
@bp.route('/<int:apartmentId>/delete', methods=('POST',))
@login_required
def delete(apartmentId):
    get_apartment(apartmentId)
    db = get_db()
    db.execute('DELETE FROM apartment WHERE apartment_id = ?', (apartmentId,))
    db.commit()
    return redirect(url_for('apartment.index'))


# PUT:  /apartment/<int: apartmentId>/update
# Update the apartment by given apartmentId
@bp.route('/<int:apartmentId>/update', methods=('POST',))
@login_required
def update(apartmentId):
    aprtment = get_apartment(apartmentId)

    if request.method == 'POST':
        name = request.form['name']
        room_number = request.form['room_number']
        bathroom_number = request.form['bathroom_number']
        street_address = request.form['street_address']
        city = request.form['city']
        state = request.form['state']
        zip = request.form['zip']
        price = request.form['price']
        sqft = request.form['sqft']
        description = request.form['description']
        photo_URL = request.form['photo_URL']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE apartment SET name = ?, room_number = ?, bathroom_number = ? , street_address = ?,  city = ?, state = ?, zip = ?, price = ?, sqtf = ?, description = ?, photo_URL = ?'
                ' WHERE apartment_id = ?',
                (name, room_number, bathroom_number, street_address, city,
                 state, zip, price, sqft, description, photo_URL, apartmentId)
            )
            db.commit()
            return redirect(url_for('apartment.index'))

    return render_template('apartment/update.html', aprtment=aprtment)
