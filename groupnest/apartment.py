from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from groupnest.auth import login_required
from groupnest.db import get_db

import logging

bp = Blueprint('apartment', __name__, url_prefix='/apartment')


# GET: /apartment Return the index page
@bp.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT *'
        ' FROM apartment'
        ' ORDER BY created DESC'
        ' LIMIT 10'
    )
    apartments = cursor.fetchall()
    
    result = []
    if apartments:
        for index in range(len(apartments)):
            apt = apartments[index]
            item = {}
            item['name'] = apt['name']
            item['room_number'] = apt['room_number']
            item['bathroom_number'] = apt['bathroom_number']
            item['street_address'] = apt['street_address']
            item['zip'] = apt['zip']
            item['city'] = apt['city']
            item['state'] = apt['state']
            item['price'] = apt['price']
            item['sqft'] = apt['sqft']
            item['description'] = apt['description']
            item['photo_URL'] = apt['photo_URL']
            result.append(item)
        return jsonify(result)
    else:
        abort(404,
              "No available apartment. Sorry! :(")


# GET: /apartment/search (zipcode)
# Get a list of apartments by searching zipcode
@bp.route('/search', methods=('GET', 'POST'))
def search():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        zip = request.form['zip']
        error = None
        if not zip:
            error = 'ZipCode is required.'

        result = []
        if error is not None:
            flash(error)
        else:
            cursor.execute(
                'SELECT *'
                ' FROM apartment'
                ' WHERE zip = %s'
                ' ORDER BY created DESC',
                (zip,)
            )
            apartments = cursor.fetchall()
            if apartments:
                # for index in range(len(apartments)):
                #     apt = apartments[index]
                #     item = {}
                #     item['name'] = apt['name']
                #     item['room_number'] = apt['room_number']
                #     item['bathroom_number'] = apt['bathroom_number']
                #     item['zip'] = apt['zip']
                #     item['city'] = apt['city']
                #     item['state'] = apt['state']
                #     item['price'] = apt['price']
                #     item['sqft'] = apt['sqft']
                #     result.append(item)
                # return jsonify(result)
                return jsonify(apartments)
            else:
                abort(404,
                      "No such apartment matching given zipcode exists in our databse. Sorry! :(")
    return redirect(url_for('apartment.index'))

# Get a apartment by apartmentId

def get_apartment(apartmentId, check_user=True):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT *'
        ' FROM apartment'
        ' WHERE apartment_id = %s',
        (apartmentId,)
    )
    apartment = cursor.fetchone()

    if apartment is None:
        abort(404, "Apartment id {0} doesn't exist.".format(apartmentId))

    # if check_user and apartment['landlord_id'] != g.user['user_id']:
    #     abort(403, "You can only modify your own apartment.")

    return apartment


# get all the nest objects associated with the given apartmentId


def get_nests(apartmentId):

    db = get_db()
    cursor = db.cursor()
    # check if the given apartmentId is valid
    cursor.execute(
        'SELECT name'
        ' FROM apartment'
        ' WHERE apartment_id = %s',
        (apartmentId,)
    )
    apartment = cursor.fetchall()
    if len(apartment) == 0:
        abort(404, "Apartment id {0} doesn't exist.".format(id))

    cursor.execute(
        'SELECT *'
        ' FROM nest'
        ' WHERE apartment_id = %s',
        (apartmentId,)
    )
    nestList = cursor.fetchall()

    return nestList

# DELETE: /apartment/<int: apartmentId>/delete
# Delete all the apartment data including nest and reservations for giving apartmentId.
@bp.route('/<int:apartmentId>/delete', methods=('POST',))
@login_required
def delete(apartmentId):
    nestList = get_nests(apartmentId)
    db = get_db()
    cursor = db.cursor()
    if nestList is not None:
        for nest in nestList:
            nestId = nest['nest_id']
            cursor.execute('DELETE FROM reservation WHERE nest_id = %s', (nestId,))
    cursor.execute('DELETE FROM nest WHERE apartment_id = %s', (apartmentId,))
    cursor.execute('DELETE FROM apartment WHERE apartment_id = %s', (apartmentId,))
    db.commit()
    return redirect(url_for('apartment.index'))


# PUT:  /apartment/<int: apartmentId>/update
# Update the apartment by given apartmentId
@bp.route('/<int:apartmentId>/update', methods=('GET', 'POST'))
@login_required
def update(apartmentId):
    apartment = get_apartment(apartmentId)
    if apartmentId != g.user['user_id']:
        abort(403, "You can only modify your own apartment.")

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
            cursor = db.cursor()
            cursor.execute(
                'UPDATE apartment SET name = %s, room_number = %s, bathroom_number = %s, street_address = %s,  city = %s, state = %s, zip = %s, price = %s, sqft = %s, description = %s, photo_URL = %s'
                ' WHERE apartment_id = %s',
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
            error = 'name is required.'
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
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO apartment (room_number, bathroom_number, street_address, city,state,zip ,price,sqft,name,description,landlord_id, photo_URL)'
                ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (room_number, bathroom_number, street_address, city, state, zip,
                 price, sqft, name, description, g.user['user_id'], photo_URL)
            )
            db.commit()

            return redirect(url_for('apartment.index'))

    return render_template('apartment/create.html')


# GET:  /apartment/<int: apartmentId>/browse
# Get the apartment by given apartmentId
@bp.route('/<int:apartmentId>/browse', methods=('GET',))
def browse(apartmentId):
    apt = get_apartment(apartmentId)
    if apt:
        item = {}
        item['room_number'] = apt['room_number']
        item['bathroom_number'] = apt['bathroom_number']
        item['zip'] = apt['zip']
        item['street_address'] = apt['street_address']
        item['city'] = apt['city']
        item['state'] = apt['state']
        item['name'] = apt['name']
        item['landlord_id'] = apt['landlord_id']

        return jsonify(item)
    else:
        abort(404, "Apartment id {0} doesn't exist.".format(apartmentId))

# GET:/apartment/ownerList
# Get the landload's apartments
@bp.route('/ownerList', methods=('GET',))
@login_required
def get_ownerList():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT a.name, a.street_address, a.price, username,room_number,bathroom_number,street_address,zip,city,state,price,sqft'
        ' FROM apartment a JOIN user u ON a.landlord_id = u.user_id'
        ' WHERE u.user_id = %s',
        (g.user['user_id'],)
    )
    ownerList = cursor.fetchall()
    if not ownerList:
        abort(404, "There is no apartments in your account:(")

    result = []
    for index in range(len(ownerList)):
        apt = ownerList[index]
        item = {}
        item['name'] = apt['name']
        item['room_number'] = apt['room_number']
        item['bathroom_number'] = apt['bathroom_number']
        item['street_address'] = apt['street_address']
        item['zip'] = apt['zip']
        item['city'] = apt['city']
        item['state'] = apt['state']
        item['price'] = apt['price']
        item['sqft'] = apt['sqft']
        result.append(item)
    return jsonify(result)

    # return "ownerList is in construction"
    return jsonify(ownerList)

# GET:/apartment/reserveList
# Return a list of reservations in a given user id.
@bp.route('/reserveList', methods=('GET',))
@login_required
def get_reservations():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT reservation_id, r.nest_id, created, accept_offer'
        ' FROM reservation r'
        ' WHERE r.tenant_id = %s',
        (g.user['user_id'],)
    )
    reserveList = cursor.fetchall()

    if reserveList is None:
        abort(404, "Nest id {0} doesn't exist or doesn't have reservations.".format(g.user['user_id']))

    result = []
    for index in range(len(reserveList)):
        apt = reserveList[index]
        item = {}
        item['reservation_id'] = apt['reservation_id']
        item['nest_id'] = apt['nest_id']
        item['created'] = apt['created']
        item['accept_offer'] = apt['accept_offer']
        result.append(item)
    return jsonify(result)