from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from groupnest.auth import login_required
from groupnest.db import get_db

bp = Blueprint('nest', __name__, url_prefix='/nest')

@bp.route('/<int:apartmentId>/fullNest')
@login_required
def get_fullNest(apartmentId):
    fullNest = fullNest(apartmentId)

    return jsonify(fullNest)

@bp.route('/<int:apartmentId>/notFullNest')
@login_required
def get_notFullNest(apartmentId):
    notFullNest = notFullNest(apartmentId)

    return jsonify(notFullNest)

@bp.route('<int:apartmentId>/allNests')
@login_required
def get_allNest(apartmentId):
    result = {}
    result['fullnest'] = fullNest(apartmentId)
    result['notFullnest'] = notFullNest(apartmentId) 
    
    return  jsonify(result)

def fullNest(apartmentId):
    result = []
    nestList = db.execute(
         'SELECT *'
        ' FROM nest'
        ' WHERE apartment_id = ?',
        (apartmentId,)
    ).fetchall()
    for nest in nestList
        res = nestTwoNumber(nest.nestId)
        if res['room_number'] == res['user_number']
            item = {}
            item['room_number'] = res['room_number']
            item['user_number'] = res['user_number']
            result.append(item)
    
    return result

def notFullNest(apartmentId):
    result = []
    nestList = db.execute(
         'SELECT *'
        ' FROM nest'
        ' WHERE apartment_id = ?',
        (apartmentId,)
    ).fetchall()
    for nest in nestList
        res = nestTwoNumber(nest.nestId)
        if res['room_number'] != res['user_number']
            item = {}
            item['room_number'] = res['room_number']
            item['user_number'] = res['user_number']
            result.append(item)
    
    return result

def nestTwoNumber(nestId):
    users = nestUser(nestId)
    apartment = db.execute(
         'SELECT room_number'
        ' FROM apartment p JOIN nest u ON p.apartment_id = u.apartment_id'
        ' WHERE n.nest_id = ?',
        (nestId,)
    ).fetchall()
    res = {}
    res['room_number'] = apartment.room_number
    res['user_number'] = users.size()

    return res 

@bp.route('/<int:nestId>')
@login_required
def nestUser(nestId):
    item = {}
    res = nestTwoNumber(nestId)
    item['room_number'] = res['room_number']
    item['user_number'] = res['user_number']
    item['user_list'] = db.execute(
        'SELECT first_name, last_name, email, gender, description'
        ' FROM reservation p JOIN user u ON p.tenant_id = u.user_id'
        ' WHERE p.nest_id = ?'
        ' AND cancelled = 0'
        ' ORDER BY created DESC',
        (nestId,)
    ).fetchall()

    return jsonify(item)

@bp.route('/reserveNest')
@login_required
def get_reserveNest():
    reservation_list = db.execute(
        'SELECT nest_id, accept_offer'
        ' FROM reservation'
        ' WHERE tenant_id = ?'
        ' ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()
    result = []
    for reservation in reservation_list
        nest_id = reservation.nest_id
        nest = db.execute(
        'SELECT apartment_id, status'
        ' FROM nest'
        ' WHERE nest_id = ?',
        (nest_id,)
        apartment = db.execute(
        'SELECT name'
        ' FROM apartment'
        ' WHERE apartment_id = ?',
        (nest.apartment_id,)
        res = nestTwoNumber(nest.nestId)
        item = {}
        item['room_number'] = res['room_number']
        item['user_number'] = res['user_number']
        item['apartment_name'] = apartment.name
        item['status'] = nest.status
        item['nest_id'] = nest_id
        result.append(item)
    ).fetchall()

    return jsonify(result)

@bp.route('/ownerNest')
@login_required
def get_ownerNest():
    result = []
    apartment_list = db.execute(
        'SELECT apartment_id, name'
        ' FROM apartment'
        ' WHERE landlord_id = ?'
        ' ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()
    for apartment in apartment_list
        item = {}
        item['fullnest'] = fullNest(apartment.apartment_id)
        item['notFullnest'] = notFullNest(apartment.apartment_id) 
        item['apartment_name'] = apartment.name
        result.append(item)

    return jsonify(result)

@bp.route('/<int:apartmentId>/create', methods=('GET', 'POST'))
@login_required
def create(apartmentId):
    if request.method == 'POST':
        db = get_db()
        db.execute(
                'INSERT INTO nest (apartment_id)'
                ' VALUES (?)',
                (apartmentId,)
        )
        db.commit()
        nest_id = db.lastrowid
        db.execute(
                'INSERT INTO reservation (nest_id, tenant_id)'
                ' VALUES (?, ?)',
                (nest_id, g['id'])
        )
        db.commit()
        return 'save successfully'

    return "create nest page"

@bp.route('/<int:nestId>/update') #(form: approve, reject，pending) 
@login_required
def update(nestId):
    if request.method == 'POST':
        decision = request.form['decision']
        error = None

        if not decision:
            error = 'Decision is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE nest SET status = ?'
                ' WHERE id = ?',
                (decision, nestId)
            )
            db.commit()
            return 'update nest status'

    return 'Hello, nest!'
