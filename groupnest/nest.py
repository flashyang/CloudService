from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from flask import Flask

from werkzeug.exceptions import abort

from groupnest.auth import login_required
from groupnest.db import get_db

import logging

bp = Blueprint('nest', __name__, url_prefix='/nest')

app = Flask(__name__)

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

    return jsonify(item)

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
    # check if the given apartmentId exists
    db = get_db()
    apartment = db.execute(
        'SELECT *'
        ' FROM apartment'
        ' WHERE apartment_id = ?',
        (apartmentId,)
    ).fetchone()

    logging.info('fetch apartment with Id %s', apartmentId)

    if apartment is None:

        logging.error('%s not found', apartmentId)
        abort(404, "Apartment not found.")
        # responseObject = {
        #     'status': 'fail',
        #     'message': 'Apartment not found.',
        # }
        # return make_response(jsonify(responseObject)), 404

    if request.method == 'POST':

        # check if the user has been added to five nests associated with the given apartment
        record = db.execute(
            'SELECT DISTINCT n.nest_id'
            ' FROM nest n JOIN reservation r ON n.nest_id = r.nest_id'
            ' WHERE r.tenant_id = ?'
            ' AND n.apartment_id = ?'
            ' ORDER BY created DESC',
            (g.user['user_id'], apartmentId)
        ).fetchall()

        logging.info(
            'user has been added in %s nests for this apartment', len(record))

        if len(record) >= 5:

            logging.error(
                'user has been added to more than 5 nests, request')

            # responseObject = {
            #     'status': 'fail',
            #     'message': 'User has already been added to five nests belong to this apartment. Please cancal the previous reservation and create a new nest again.',
            # }
            # return make_response(jsonify(responseObject)), 403
            #abort(403, 'User has already been added to five nests belong to this apartment. Please cancal the previous reservation and create a new nest again.')
            error = 'User has already been added to five nests belong to this apartment. Please cancal the previous reservation and create a new nest again.'
            flash(error)
        else:
            nest_id = db.execute(
                'INSERT INTO nest (apartment_id)'
                ' VALUES (?)',
                (apartmentId,)
            ).lastrowid

            logging.info('nest with id %s created', nest_id)

            db.execute(
                'INSERT INTO reservation (nest_id, tenant_id)'
                ' VALUES (?, ?)',
                (nest_id, g.user['user_id'])
            )
            db.commit()

            logging.info('reservation created for user %s and nest %s', g.user['user_id'], nest_id)

            url = 'apartment/'+ apartmentId +'/browse'
            return redirect(url_for(url))

            # responseObject = {
            #     'status': 'success',
            #     'message': 'Successfully created new reservasion.',
            # }
            # return make_response(jsonify(responseObject)), 201
    # responseObject = {
    #     'status': 'success',
    #     'message': 'Successfully get create nest',
    # }
    # return make_response(jsonify(responseObject)), 200
    return render_template('nest/create.html')


# Updates the nest status when the landlord approve or reject a full nest
# Only available for registered user
# (form: approve, reject, pending)
@bp.route('/<int:nestId>/update', methods=['GET', 'POST'])
@login_required
def update(nestId):
    db = get_db()
    # check if the current nestId exists and the nest status is PENDING
    cur_nest = db.execute(
        'SELECT status'
        ' FROM nest'
        ' WHERE nest_id = ?'
        (nestId,)
    ).fetchone()

    logging.info('fetch nest with Id %s', nestId)

    if cur_nest is None:
        # abort(404, "Nest not found")
        logging.error('%s not found', nestId)
        responseObject = {
            'status': 'fail',
            'message': 'Nest not found.',
        }
        return make_response(jsonify(responseObject)), 404

    if request.method == 'POST':
        decision = request.form['decision']
        error = None

        if not decision:
            logging.error('No decision provided. Error message sent.')
            error = 'Decision is required.'
            responseObject = {
                'status': 'fail',
                'message': error
            }
            return make_response(jsonify(responseObject)), 403

        if cur_nest['status'] != 'PENDING':
            error = 'Cannot change nest status that is not PENDING'
            logging.error(
                'target nest status is %s, cannot change to other status.', cur_nest['status'])
            responseObject = {
                'status': 'fail',
                'message': error
            }
            return make_response(jsonify(responseObject)), 403

        # check if current user is the landlord of the apartment associated with the nest with the given nest_id
        owner = db.execute(
            'SELECT landlord_id'
            ' FROM apartment a JOIN nest n ON a.apartment_id = n.apartment_id'
            ' WHERE n.nest_id = ?',
            (nestId,)
        ).fetchone()
        if owner['landlord_id'] != g.user['user_id']:
            error = 'Current user is not authorized to alter the status of this nest.'
            logging.error('current user id is %s, not equal to the landloard id %s',
                          (owner['landlord_id'], g.user['user_id']))
            responseObject = {
                'status': 'fail',
                'message': error
            }
            return make_response(jsonify(responseObject)), 403

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
            logging.error(error)
            responseObject = {
                'status': 'fail',
                'message': error
            }
            return make_response(jsonify(responseObject)), 403

        # check if the given nest is full
        two_number = nestTwoNumber(nestId)
        if two_number['room_number'] != two_number['user_number']:
            error = 'This nest is not full yet, landlord cannot alter nest status'
            logging.error('nest has %s/%s users added. Cannot change the status of a nest to be filled',
                          (two_number['user_number'], two_number['room_number']))
            responseObject = {
                'status': 'fail',
                'message': error
            }
            return make_response(jsonify(responseObject)), 403

        # if error is not None:
        #     return error
        # else:
        db.execute(
            'UPDATE nest SET status = ?'
            ' WHERE nest_id = ?',
            (decision, nestId)
        )
        db.commit()
        logging.info('updated nest %s status', nestId)
        responseObject = {
            'status': 'succeed',
            'message': 'updated nest status'
        }
        return make_response(jsonify(responseObject)), 200

    responseObject = {
        'status': 'succeed',
        'message': 'get update nest'
    }
    return make_response(jsonify(responseObject)), 200


# TODO: check input valid(id) && error handeling && log, unit test; API doc; database; cache; pipeline;
