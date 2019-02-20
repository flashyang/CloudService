from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from groupnest.auth import login_required
from groupnest.db import get_db

bp = Blueprint('nest', __name__, url_prefix='/nest')

# Given apartmentId, get all associated full nest information, return number of room in the apartment, number of reservations alive in each nest, status of each nest.
# publicly available
@bp.route('/<int:apartmentId>/fullNest')
def get_fullNest(apartmentId):
    fullNest = fullNest_helper(apartmentId)

    return jsonify(fullNest)

# Given apartmentId, get all associated nest information for the nests that are not full return number of room in the apartment, number of reservations alive in each nest, status of each nest.
# publicly available
@bp.route('/<int:apartmentId>/notFullNest')
def get_notFullNest(apartmentId):
    notFullNest = notFullNest_helper(apartmentId)

    return jsonify(notFullNest)

# Given apartmentId, get all associated nest information, return number of room in the apartment, number of reservations alive in each nest, status of each nest.
# publicly available
@bp.route('<int:apartmentId>/allNests')
def get_allNest(apartmentId):
    result = {}
    result['fullnest'] = fullNest_helper(apartmentId)
    result['notFullnest'] = notFullNest_helper(apartmentId)

    return jsonify(result)

# get all the nest objects associated with the given apartmentId


def get_nests(apartmentId):
    # check if the given apartmentId is valid
    db = get_db()
    apartment = db.execute(
        'SELECT name'
        ' FROM apartment'
        ' WHERE apartment_id = ?',
        (apartmentId,)
    ).fetchall()
    if len(apartment) == 0:
        abort(404, "Apartment id {0} doesn't exist.".format(id))

    nestList = db.execute(
        'SELECT *'
        ' FROM nest'
        ' WHERE apartment_id = ?',
        (apartmentId,)
    ).fetchall()

    return nestList


# Given apartmentId, get all associated full nest information, return number of room in the apartment, number of reservations alive in each nest, status of each nest.
# publicly available
def fullNest_helper(apartmentId):
    result = []
    nestList = get_nests(apartmentId)
    for index in range(len(nestList)):
        nest = nestList[index]
        res = nestTwoNumber(nest['nest_id'])
        if res['room_number'] == res['user_number']:
            item = {}
            item['room_number'] = res['room_number']
            item['user_number'] = res['user_number']
            item['nest_id'] = nest['nest_id']
            result.append(item)

    return result

# Given apartmentId, get all associated nest information for the nests that are not full return number of room in the apartment, number of reservations alive in each nest, status of each nest.
# publicly available


def notFullNest_helper(apartmentId):
    result = []
    nestList = get_nests(apartmentId)
    for index in range(len(nestList)):
        nest = nestList[index]
        res = nestTwoNumber(nest['nest_id'])
        if res['room_number'] != res['user_number']:
            item = {}
            item['room_number'] = res['room_number']
            item['user_number'] = res['user_number']
            item['nest_id'] = nest['nest_id']
            result.append(item)

    return result

# Given nestId, get number of room in the associated apartment and number of reservations alive


def nestTwoNumber(nestId):
    users = get_nestUser(nestId)  # add method
    apartment = get_apartment(nestId)
    res = {}
    res['room_number'] = apartment['room_number']
    res['user_number'] = len(users)
    return res


# Given nestId, get the associated apartment
def get_apartment(nestId):
    db = get_db()
    apartment = db.execute(
        'SELECT name, room_number, n.apartment_id'
        ' FROM apartment p JOIN nest n ON p.apartment_id = n.apartment_id'
        ' WHERE n.nest_id = ?',
        (nestId,)
    ).fetchone()
    return apartment


# Given nestId, get users added in the nest. (user info: first_name, last_name, email, gender, description)
def get_nestUser(nestId):
    db = get_db()
    user = db.execute(
        'SELECT first_name, last_name, email, gender, description'
        ' FROM reservation p JOIN user u ON p.tenant_id = u.user_id'
        ' WHERE p.nest_id = ?'
        # ' AND p.cancelled = 0'
        ' ORDER BY created DESC',
        (nestId,)
    ).fetchall()
    return user


# Given nestId, get number of rooms in the associated apartment, number of reservations alive and the user information for the reservations alive(user info: first_name, last_name, email, gender, description)
# Only available for registered user
@bp.route('/<int:nestId>')
@login_required
def nestUser(nestId):
    res = nestTwoNumber(nestId)
    item = {}
    item['room_number'] = res['room_number']
    item['user_list'] = get_nestUser(nestId)
    item['user_number'] = res['user_number']

    return render_template('nest/detail.html', users=item['user_list'], room_number=item['room_number'], user_number=res['user_number'])

# For the current user, get all associated nests info (nest info: number of rooms in the apartment, number of users currently added in the nest, apartment name, nest status, nest_id)
# Only available for registered user
@bp.route('/reserveNest')
@login_required
def get_reserveNest():
    db = get_db()
    reservation_list = db.execute(
        'SELECT nest_id, accept_offer'
        ' FROM reservation'
        ' WHERE tenant_id = ?'
        ' ORDER BY created DESC',
        (g.user['user_id'],)
    ).fetchall()
    result = []
    for index in range(len(reservation_list)):
        reservation = reservation_list[index]
        nest_id = reservation['nest_id']
        nest = db.execute(
            'SELECT apartment_id, status'
            ' FROM nest'
            ' WHERE nest_id = ?',
            (nest_id,)
        ).fetchone()
        apartment = db.execute(
            'SELECT name'
            ' FROM apartment'
            ' WHERE apartment_id = ?',
            (nest['apartment_id'],)
        ).fetchone()
        res = nestTwoNumber(nest_id)
        item = {}
        item['room_number'] = res['room_number']
        item['user_number'] = res['user_number']
        item['apartment_name'] = apartment['name']
        item['status'] = nest['status']
        item['nest_id'] = nest_id
        result.append(item)

    return jsonify(result)

# For the current user, get all the nests info for each apartment this user owns. Nest info includes number of rooms in the apartment, number of reservations alive in each nest, status of each nest.
# Only available for registered user
@bp.route('/ownerNest')
@login_required
def get_ownerNest():
    result = []
    db = get_db()
    apartment_list = db.execute(
        'SELECT apartment_id, name'
        ' FROM apartment'
        ' WHERE landlord_id = ?'
        ' ORDER BY created DESC',
        (g.user['user_id'],)
    ).fetchall()
    for index in range(len(apartment_list)):
        apartment = apartment_list[index]
        item = {}
        item['fullnest'] = fullNest_helper(apartment['apartment_id'])
        item['notFullnest'] = notFullNest_helper(apartment['apartment_id'])
        item['apartment_name'] = apartment['name']
        result.append(item)

    return jsonify(result)

# Creates a new nest for the apartment with the given apartmentId. Also creates a new reservation.
# Only available for registered user
@bp.route('/<int:apartmentId>/create', methods=('GET', 'POST'))
@login_required
def create(apartmentId):
    if request.method == 'POST':
        print('start')
        db = get_db()
        error = None
        # check if the user has been added to one of the nest associated with the given apartment
        record = db.execute(
            'SELECT apartment_id'
            ' FROM nest n JOIN reservation r ON n.nest_id = r.nest_id'
            ' WHERE r.tenant_id = ?'
            ' AND n.apartment_id = ?'
            ' ORDER BY created DESC',
            (g.user['user_id'], apartmentId)
        ).fetchall()
        print(g.user['user_id'])
        if len(record) != 0:
            error = 'User has already been added to one nest belong to this apartment. Please cancal the previous reservation and create a new nest again.'

        if error is not None:
            print(error)
            flash(error)
        else:
            print('execute db')
            nest_id = db.execute(
                'INSERT INTO nest (apartment_id)'
                ' VALUES (?)',
                (apartmentId,)
            ).lastrowid
            db.execute(
                'INSERT INTO reservation (nest_id, tenant_id)'
                ' VALUES (?, ?)',
                (nest_id, g.user['user_id'])
            )
            db.commit()
            print('saved')
            return 'save successfully'

    return render_template('nest/create.html')


# Updates the nest status when the landlord approve or reject a full nest
# Only available for registered user
# (form: approve, reject，pending)
@bp.route('/<int:nestId>/update', methods=['GET', 'POST'])
@login_required
def update(nestId):
    if request.method == 'POST':
        decision = request.form['decision']
        error = None

        if not decision:
            error = 'Decision is required.'

        # check if current user is the landlord of the apartment associated with the nest with the given nest_id
        db = get_db()
        owner = db.execute(
            'SELECT landlord_id'
            ' FROM apartment a JOIN nest n ON a.apartment_id = n.apartment_id'
            ' WHERE n.nest_id = ?',
            (nestId,)
        ).fetchone()
        if owner['landlord_id'] != g.user['user_id']:
            error = 'Current user is not authorized to alter the status of this nest.'

        # check if the landlord has already approved a nest
        apartment = get_apartment(nestId)
        approved_nest = db.execute(
            'SELECT *'
            ' FROM nest n'
            ' WHERE n.apartment_id = ?'
            ' AND status = ?',
            (apartment['apartment_id'], 'APPROVED')
        ).fetchall()
        if len(approved_nest) != 0 and request.form['decision'] == 'APPROVED':
            error = 'Landlord has already approved one nest'

        # check if the given nest is full
        two_number = nestTwoNumber(nestId)
        if two_number['room_number'] != two_number['user_number']:
            error = 'Given nest is not full yet, landlord cannot alter nest status yet'

        if error is not None:
            print(error)
            flash(error)
        else:
            db.execute (
                'UPDATE nest SET status = ?'
                ' WHERE nest_id = ?',
                (decision, nestId)
            )
            db.commit()
            return 'update nest status'

    return 'Hello, nest!'


# TODO: check input valid(id) && error handeling && log, unit test; API doc; database; cache; pipeline;
