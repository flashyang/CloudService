from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from groupnest.auth import login_required
from groupnest.db import get_db


bp = Blueprint('apartment', __name__, url_prefix='/apartment')


# GET: /apartment Return the index page
@bp.route('/')
def index():
    db = get_db()
    apartments = db.execute(
        'SELECT *'
        ' FROM apartment'
        ' ORDER BY created DESC'
        ' LIMIT 10'
    ).fetchall()
    return render_template('apartment/index.html', apartments=apartments)

# GET: /apartment/search (zipcode)
# Get a list of apartments by searching zipcode
@bp.route('/search', methods=('GET', 'POST'))
def search():
    db = get_db()
    if request.method == 'POST':
        zip = request.form['zip']
        error = None
        if not zip:
            error = 'ZipCode is required.'

        if error is not None:
            flash(error)
        else:
            apartments = db.execute(
                'SELECT *'
                ' FROM apartment'
                ' WHERE zip = ?'
                ' ORDER BY created DESC',
                (zip,)
            ).fetchall()
            if apartments:
                return "Searching result is in construction"
            else:
                abort(404,
                      "No such apartment matching given zipcode exists in our databse. Sorry! :(")
    return redirect(url_for('apartment.index'))

# Get a apartment by apartmentId


def get_apartment(apartmentId):
    apartment = get_db().execute(
        'SELECT *'
        ' FROM apartment'
        ' WHERE apartment_id = ?',
        (apartmentId,)
    ).fetchone()

    if apartment is None:
        abort(404, "Apartment id {0} doesn't exist.".format(apartmentId))

    return apartment

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
@bp.route('/<int:apartmentId>/update', methods=('GET', 'POST'))
@login_required
def update(apartmentId):
    apartment = get_apartment(apartmentId)

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
                'UPDATE apartment SET name = ?, room_number = ?, bathroom_number = ? , street_address = ?,  city = ?, state = ?, zip = ?, price = ?, sqft = ?, description = ?, photo_URL = ?'
                ' WHERE apartment_id = ?',
                (name, room_number, bathroom_number, street_address, city,
                 state, zip, price, sqft, description, photo_URL, apartmentId)
            )
            db.commit()
            return redirect(url_for('apartment.index'))

    return render_template('apartment/update.html', apartment=apartment)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new post for the current user."""
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
            error = 'title is required.'
        if not room_number:
            error = 'room number is required.'

        if not bathroom_number:
            error = 'bathroom number is required.'
        if not street_address:
            error = 'street address is required.'
        if not city:
            error = 'city is required.'
        if not state:
            error = 'state is required.'
        if not zip:
            error = 'zip is required.'
        if not price:
            error = 'price is required.'
        if not sqft:
            error = 'sqft is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO apartment (room_number, bathroom_number, street_address, city,state,zip ,price,sqft,name,description,landlord_id, photo_URL)'
                ' VALUES (?, ?, ?,?,?, ?, ?,?,?,?,?,?)',
                (room_number, bathroom_number, street_address, city, state, zip,
                 price, sqft, name, description, g.user['user_id'], photo_URL)
            )
            db.commit()
            return redirect(url_for('apartment.index'))

    return render_template('apartment/create.html')


# GET:/apartment/ownerList
# Get the landload's apartments
@bp.route('/ownerList', methods=('GET',))
@login_required
def get_ownerList():
    db = get_db()
    ownerList = db.execute(
        'SELECT a.name, a.street_address, a.price, username'
        ' FROM apartment a JOIN user u ON a.landlord_id = u.user_id'
        ' WHERE u.user_id = ?',
        (g.user['user_id'],)
    ).fetchall()
    if not ownerList:
        abort(404, "There is no apartments in your account:(")

    return "ownerList is in construction"

# GET:/apartment/reserveList
# Get the user's reservations
@bp.route('/reserveList', methods=('GET',))
@login_required
def get_reserveList():
    db = get_db()
    reserveList = db.execute(
        'SELECT r.nest_id,r.created,r.cancelled, username'
        ' FROM reservation r JOIN user u ON r.tenant_id = u.user_id'
        ' WHERE u.user_id = ?',
        (g.user['user_id'],)
    ).fetchall()
    if not reserveList:
        abort(404, "There is no reservations in your account:(")

    return "reserveList is in construction"
