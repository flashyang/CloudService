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

# Given apartmentId, get all associated full nest information, 
# return number of room in the apartment, number of reservations alive in each nest, 
# status of each nest.
# publicly available
@bp.route('/<int:apartmentId>/fullNest')
def get_fullNest(apartmentId):
    fullNest = fullNest_helper(apartmentId)

    return jsonify(fullNest)

# Given apartmentId, get all associated nest information for the nests that are not full 
# return number of room in the apartment, number of reservations alive in each nest, 
# status of each nest.
# publicly available
@bp.route('/<int:apartmentId>/notFullNest')
def get_notFullNest(apartmentId):
    notFullNest = notFullNest_helper(apartmentId)

    return jsonify(notFullNest)

# Given apartmentId, get all associated nest information, return number of 
# room in the apartment, number of reservations alive in each nest, status of each nest.
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
    cursor = db.cursor()
    cursor.execute(
        """SELECT name
        FROM apartment
        WHERE apartment_id = %s""",
        (apartmentId,)
    )
    apartment = cursor.fetchall()
    if len(apartment) == 0:
        abort(404, "Apartment id {0} doesn't exist.".format(id))

    cursor.execute(
        """SELECT *
        FROM nest
        WHERE apartment_id = %s""",
        (apartmentId,)
    )
    nestList = cursor.fetchall()

    return nestList


# Given apartmentId, get all associated full nest information, return number of 
# room in the apartment, number of reservations alive in each nest, status of each nest.
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

# Given apartmentId, get all associated nest information for the nests that are not 
# full return number of room in the apartment, number of reservations alive in each nest, 
# status of each nest.
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
    cursor = db.cursor()
    cursor.execute(
        """SELECT name, room_number, n.apartment_id
        FROM apartment p JOIN nest n ON p.apartment_id = n.apartment_id
        WHERE n.nest_id = %s""",
        (nestId,)
    )
    apartment = cursor.fetchone()
    return apartment


# Given nestId, get users added in the nest. (user info: first_name, last_name, email, 
# gender, description)
def get_nestUser(nestId):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """SELECT username, first_name, last_name, email, gender, description
        FROM reservation p JOIN user u ON p.tenant_id = u.user_id
        WHERE p.nest_id = %s
        ORDER BY created DESC""",
        (nestId,)
    )
    users = cursor.fetchall()
    # columns = ['username', 'first_name', 'last_name', 'email', 'gender', 'description']
    res = []
    for user in users:
        # res.append(dict(zip(columns, user)))
        res.append(user)
    return res


# Given nestId, get number of rooms in the associated apartment, number of reservations 
# alive and the user information for the reservations alive(user info: first_name, last_name, 
# email, gender, description)
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

# For the current user, get all associated nests info (nest info: number of rooms 
# in the apartment, number of users currently added in the nest, apartment name, nest status, nest_id)
# Only available for registered user
@bp.route('/reserveNest')
@login_required
def get_reserveNest():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """SELECT nest_id, accept_offer
        FROM reservation
        WHERE tenant_id = %s
        ORDER BY created DESC""",
        (g.user['user_id'],)
    )
    reservation_list = cursor.fetchall()
    result = []
    for index in range(len(reservation_list)):
        reservation = reservation_list[index]
        nest_id = reservation['nest_id']
        cursor.execute(
            """SELECT apartment_id, status
            FROM nest
            WHERE nest_id = %s""",
            (nest_id,)
        )
        nest = cursor.fetchone()
        cursor.execute(
            """SELECT name
            FROM apartment
            WHERE apartment_id = %s""",
            (nest['apartment_id'],)
        )
        apartment = cursor.fetchone()
        res = nestTwoNumber(nest_id)
        item = {}
        item['room_number'] = res['room_number']
        item['user_number'] = res['user_number']
        item['apartment_name'] = apartment['name']
        item['status'] = nest['status']
        item['nest_id'] = nest_id
        result.append(item)

    return jsonify(result)

# For the current user, get all the nests info for each apartment this user owns. 
# Nest info includes number of rooms in the apartment, number of reservations alive in each nest, 
# status of each nest.
# Only available for registered user
@bp.route('/ownerNest')
@login_required
def get_ownerNest():
    result = []
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """SELECT apartment_id, name
        FROM apartment
        WHERE landlord_id = %s
        ORDER BY created DESC""",
        (g.user['user_id'],)
    )
    apartment_list = cursor.fetchall()
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
    cursor = db.cursor()
    cursor.execute(
        """SELECT *
        FROM apartment
        WHERE apartment_id = %s""",
        (apartmentId,)
    )
    apartment = cursor.fetchone()

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
        cursor.execute(
            """SELECT DISTINCT n.nest_id
            FROM nest n JOIN reservation r ON n.nest_id = r.nest_id
            WHERE r.tenant_id = %s
            AND n.apartment_id = %s""",
            # ORDER BY created DESC""",
            (g.user['user_id'], apartmentId)
        )
        record = cursor.fetchall()

        logging.info(
            'user has been added in %s nests for this apartment', len(record))

        if len(record) >= 5:

            logging.error(
                'user has been added to more than 5 nests, request')

            abort(403, 'User has already been added to five nests belong to this apartment. Please cancal the previous reservation and create a new nest again.')
        else:
            cursor.execute(
                'INSERT INTO nest (apartment_id)'
                ' VALUES (%s)',
                (apartmentId,)
            )
            nest_id = cursor.lastrowid

            logging.info('nest with id %s created', nest_id)

            cursor.execute(
                """INSERT INTO reservation (nest_id, tenant_id)
                VALUES (%s, %s)""",
                (nest_id, g.user['user_id'])
            )
            db.commit()

            logging.info('reservation created for user %s and nest %s', g.user['user_id'], nest_id)

            return redirect(url_for('nest.nestUser', nestId=nest_id))

    return render_template('nest/create.html')


# Updates the nest status when the landlord approve or reject a full nest
# Only available for registered user
# (form: approve, reject, pending)
@bp.route('/<int:nestId>/update', methods=['GET', 'POST'])
@login_required
def update(nestId):
    db = get_db()
    cursor = db.cursor()
    # check if the current nestId exists and the nest status is PENDING
    cursor.execute(
        """SELECT status
        FROM nest
        WHERE nest_id = %s""",
        (nestId,)
    )
    cur_nest = cursor.fetchone()

    logging.info('fetch nest with Id %s', nestId)

    if cur_nest is None:
        logging.error('%s not found', nestId)
        abort(404, "Nest not found")

    if request.method == 'POST':
        decision = request.form['decision']
        error = None

        if not decision:
            logging.error('No decision provided. Error message sent.')
            abort(404, "Decision is required.")

        if cur_nest['status'] != 'PENDING':
            logging.error(
                'target nest status is %s, cannot change to other status.', cur_nest['status'])
            abort(403, 'Cannot change nest status that is not PENDING')

        # check if current user is the landlord of the apartment associated with the nest with the given nest_id
        cursor.execute(
            """SELECT landlord_id
            FROM apartment a JOIN nest n ON a.apartment_id = n.apartment_id
            WHERE n.nest_id = %s""",
            (nestId,)
        )
        owner = cursor.fetchone()
        if owner['landlord_id'] != g.user['user_id']:
            error = 'Current user is not authorized to alter the status of this nest.'
            logging.error('current user id is %s, not equal to the landloard id %s',
                          owner['landlord_id'], g.user['user_id'])
            abort(403, error)

        # check if the landlord has already approved a nest
        apartment = get_apartment(nestId)
        cursor.execute(
            """SELECT *
            FROM nest n
            WHERE n.apartment_id = %s
            AND status = %s""",
            (apartment['apartment_id'], 'APPROVED')
        )
        approved_nest = cursor.fetchall()

        if len(approved_nest) != 0 and request.form['decision'] == 'APPROVED':
            error = 'Landlord has already approved one nest'
            logging.error(error)
            abort(403, error)

        # check if the given nest is full
        two_number = nestTwoNumber(nestId)
        if two_number['room_number'] != two_number['user_number']:
            error = 'This nest is not full yet, landlord cannot alter nest status'
            logging.error('nest has %s/%s users added. Cannot change the status of a nest to be filled',
                          two_number['user_number'], two_number['room_number'])
            abort(403, error)

        # if error is not None:
        #     return error
        # else:
        cursor.execute(
            """UPDATE nest SET status = %s
            WHERE nest_id = %s""",
            (decision, nestId)
        )
        db.commit()
        logging.info('updated nest %s status', nestId)
        redirect(url_for('nest.nestUser', nestId=nestId))
        #abort(200, 'updated nest status')

    return redirect(url_for('nest.nestUser', nestId=nestId))


# TODO: check input valid(id) && error handeling && log, unit test; API doc; database; cache; pipeline;
