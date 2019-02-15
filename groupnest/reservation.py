from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from groupnest.auth import login_required
from groupnest.db import get_db
import json

bp = Blueprint('reservation', __name__, url_prefix='/reservation')

'''
Create a new reservation in the given nest for login user.
'''
@bp.route('/create/nest_id/<int:nest_id>', methods=('POST',))
@login_required
def create(nest_id):
    if not is_nest_full(nest_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO reservation (nest_id, tenant_id)'
            ' VALUES (?, ?)',
            (nest_id, g.user['user_id'])
        )
        db.commit()
        rv = get_reservation(cursor.lastrowid)
        row_headers = ['reservation_id', 'nest_id', 'tenant_id', 'accept_offer']
        json_data = dict(zip(row_headers, rv))
        return json.dumps(json_data)
    else :
        error = "Can't reserve, this nest is full."
        flash(error)
        return error

    # return redirect(url_for('nest.index'))

'''
Return a list of reservations in a given nest.
'''
def get_reservations(nest_id):
    reservations = get_db().execute(
        'SELECT reservation_id, r.nest_id, tenant_id, created, accept_offer, apartment_id, status'
        ' FROM reservation r JOIN nest n ON r.nest_id = n.nest_id'
        ' WHERE r.nest_id = ?',
        (nest_id,)
    ).fetchall()

    if reservations is None:
        abort(404, "Nest id {0} doesn't exist or doesn't have reservations.".format(nest_id))

    return reservations

'''
Return the apartment associated with given nest
'''
def get_apartment(nest_id):
    apartment = get_db().execute(
        'SELECT n.apartment_id, room_number'
        ' FROM nest n JOIN apartment a ON n.apartment_id = a.apartment_id'
        ' WHERE nest_id = ?',
        (nest_id,)
    ).fetchone()
    if apartment is None:
        abort(404, "Nest id {0} doesn't exist or doesn't have an associated appartment.".format(nest_id))

    return apartment

'''
Check if a nest is full.
If the number of reservations in the nest equals the room number of that apartment, return true.
'''
def is_nest_full(nest_id):
    reservations = get_reservations(nest_id)
    apartment = get_apartment(nest_id)

    return len(reservations) == apartment['room_number']

'''
Return a reservation for a given reservation id.
'''
def get_reservation(reservation_id, check_user=True):
    reservation = get_db().execute(
        'SELECT reservation_id, nest_id, tenant_id, accept_offer'
        ' FROM reservation'
        ' WHERE reservation_id = ?',
        (reservation_id,)
    ).fetchone()

    if reservation is None:
        abort(404, "Reservation id {0} doesn't exist.".format(reservation_id))

    if check_user and reservation['tenant_id'] != g.user['user_id']:
        abort(403, "You can only modify your own reservation.")

    return reservation

'''
Accept offer (accept offer = 1) when the nest is approved by landlord.
'''    
@bp.route('/<int:reservation_id>/accept_offer', methods=('POST',))
@login_required
def accept_offer(reservation_id):
    reservation = get_reservation(reservation_id)
    nest = get_nest(reservation['nest_id'])

    if nest['status'] != 'APPROVED':
        abort(403, "Can't accept offer without approval from landlord.")

    db = get_db()
    db.execute(
        'UPDATE reservation SET accept_offer = ?'
        'WHERE reservation_id = ?',
        (1, reservation_id)
    )
    db.commit()
    rv = get_reservation(reservation_id)
    row_headers = ['reservation_id', 'nest_id', 'tenant_id', 'accept_offer']
    json_data = dict(zip(row_headers, rv))
    return json.dumps(json_data)
    # return redirect(url_for('nest.index'))

'''
Delete the reservation for a given reservation id.
Things to check:
1. Once accepted offer (reservation's accept offer = 1), can't delete this reservation.
2. If the nest's status is APPROVED, update all the nests associated with the same apartment to be PENDING.
3. If the nest become empty after cancel the reservation, delete the nest as well.
   Else update the rest reservations in the nest to be accept_offer = 0
'''
@bp.route('/<int:reservation_id>/delete', methods=('POST',))
@login_required
def delete(reservation_id):
    error = []
    reservation = get_reservation(reservation_id)
    # Can't delet reservation that already accepted offer
    if reservation['accept_offer'] == 1:
        abort(403, "You can't cancel a reservation once accept offer.")

    db = get_db()
    db.execute('DELETE FROM reservation WHERE reservation_id = ?', (reservation_id,))
    error.append("Delete reservation id {0}".format(reservation_id))

    # Update all the nests associate with this apartment to be pending, if previous nest status is approved
    nest = get_nest(reservation['nest_id'])
    if nest['status'] == "APPROVED":
        nests = get_nests(nest['apartment_id'])
        print("nests type: " + str(type(nests)) + "  number of nests: " + str(len(nests)))

        for n in nests:
            print("test: " + str(n['nest_id']))
            db.execute(
                'UPDATE nest SET status = ?'
                ' WHERE nest_id = ?',
                ("PENDING", n['nest_id'])
            )
        error.append("Nest status changed from APPROVED to PENDING.")

    reservations = get_reservations(reservation['nest_id'])
    # Delete empty nest
    if len(reservations) == 0:
        db.execute('DELETE FROM nest WHERE nest_id = ?', (reservation['nest_id'],))
        error.append("Delete empty nest.")
    # Update the rest reservations in the nest to be "not accept offer"
    else:
        for r in reservations:
            db.execute(
                'UPDATE reservation SET accept_offer = ?'
                'WHERE reservation_id = ?',
                (0, r['reservation_id'])
            )
        error.append("Other reservation's accept_offer set to be 0.")
    db.commit()

    return str(error)

'''
Return the nest for a given nest id.
'''
def get_nest(nest_id):
    nest = get_db().execute(
        'SELECT *'
        ' FROM nest'
        ' WHERE nest_id = ?',
        (nest_id,)
    ).fetchone()

    if nest is None:
        abort(404, "Nest id {0} doesn't exist.".format(nest_id))

    return nest

'''
Return a list of nests associated with a given apartment.
'''
def get_nests(apartment_id):
    nests = get_db().execute(
        'SELECT *'
        ' FROM nest'
        ' WHERE apartment_id = ?',
        (apartment_id,)
    ).fetchall()

    if nests is None:
        abort(404, "No nest associated with apartment id {0}.".format(apartment_id))

    return nests

