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
A user is not able to make a new reservation if he joined 5 nests.
'''
@bp.route('/create/nest_id/<int:nest_id>', methods=('POST',))
@login_required
def create(nest_id):
    nest = get_nest(nest_id)
    if  get_num_of_nests_in_one_apartment(g.user['user_id'], nest['apartment_id']) >= 5:
        abort(403, "You can only join five nests under one apartment.")

    if not is_nest_full(nest_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO reservation (nest_id, tenant_id)
            VALUES (%s, %s)""",
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

'''
Return the number of nests the user has joined in the given apartment.
'''
def get_num_of_nests_in_one_apartment(user_id, apartment_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """SELECT COUNT(DISTINCT r.nest_id) c
        FROM reservation r JOIN nest n ON r.nest_id = n.nest_id
        WHERE r.tenant_id = %s and n.apartment_id = %s""",
        (user_id, apartment_id)
    )
    num_of_nests = cursor.fetchone()

    print("number of nests in apartment ", apartment_id, " that user ", user_id, " joined is: ", num_of_nests['c'])
    return num_of_nests['c']

'''
Return a list of reservations in a given nest.
'''
def get_reservations(nest_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """SELECT reservation_id, r.nest_id, tenant_id, created, accept_offer, apartment_id, status
        FROM reservation r JOIN nest n ON r.nest_id = n.nest_id
        WHERE r.nest_id = %s""",
        (nest_id,)
    )
    reservations = cursor.fetchall()

    if reservations is None:
        abort(404, "Nest id {0} doesn't exist or doesn't have reservations.".format(nest_id))

    return reservations

'''
Return the apartment associated with given nest
'''
def get_apartment(nest_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """SELECT n.apartment_id, room_number
        FROM nest n JOIN apartment a ON n.apartment_id = a.apartment_id
        WHERE nest_id = %s""",
        (nest_id,)
    )
    apartment = cursor.fetchone()
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
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """SELECT reservation_id, nest_id, tenant_id, accept_offer
        FROM reservation
        WHERE reservation_id = %s""",
        (reservation_id,)
    )
    reservation = cursor.fetchone()

    if reservation is None:
        abort(404, "Reservation id {0} doesn't exist.".format(reservation_id))

    if check_user and reservation['tenant_id'] != g.user['user_id']:
        abort(403, "You can only modify your own reservation.")

    return reservation

'''
Accept offer (set accept offer = 1) when the nest is approved by landlord.
If this is the last person accept offer, change the status of other nest to be rejected.
'''    
@bp.route('/<int:reservation_id>/accept_offer', methods=('PUT',))
@login_required
def accept_offer(reservation_id):
    reservation = get_reservation(reservation_id)
    nest = get_nest(reservation['nest_id'])

    if nest['status'] != 'APPROVED':
        abort(403, "Can't accept offer without approval from landlord.")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """UPDATE reservation SET accept_offer = %s
        WHERE reservation_id = %s""",
        (1, reservation_id)
    )

    '''
    if this is the last person in the nest who accept offer, 
    change the other nests in the associated apartment to be rejected.
    '''
    if all_accept_offer(nest['nest_id']):
        nests = get_nests(nest['apartment_id'])
        for n in nests:
            if n['nest_id'] != nest['nest_id']:
                cursor.execute(
                    """UPDATE nest SET status = %s
                    WHERE nest_id = %s""",
                    ('REJECTED', n['nest_id'])
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
@bp.route('/<int:reservation_id>/delete', methods=('DELETE',))
@login_required
def delete(reservation_id):
    error = []
    reservation = get_reservation(reservation_id)
    # Can't delet reservation that already accepted offer
    if reservation['accept_offer'] == 1:
        abort(403, "You can't cancel a reservation once accept offer.")

    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM reservation WHERE reservation_id = %s', (reservation_id,))
    error.append("Delete reservation id {0}".format(reservation_id))

    # Update the nest to be pending, if previous status is approved.
    nest = get_nest(reservation['nest_id'])
    if nest['status'] == "APPROVED":
        cursor.execute(
            """UPDATE nest SET status = %s
            WHERE nest_id = %s""",
            ("PENDING", nest['nest_id'])
        )
    error.append("Nest status changed from APPROVED to PENDING.")

    reservations = get_reservations(reservation['nest_id'])
    # Delete empty nest
    if len(reservations) == 0:
        cursor.execute('DELETE FROM nest WHERE nest_id = %s', (reservation['nest_id'],))
        error.append("Delete empty nest.")
    # Update the rest reservations in the nest to be "not accept offer"
    else:
        for r in reservations:
            cursor.execute(
                """UPDATE reservation SET accept_offer = %s
                WHERE reservation_id = %s""",
                (0, r['reservation_id'])
            )
        error.append("Other reservation's accept_offer set to be 0.")
    db.commit()

    return str(error)

'''
Return the nest for a given nest id.
'''
def get_nest(nest_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """SELECT *
        FROM nest
        WHERE nest_id = %s""",
        (nest_id,)
    )
    nest = cursor.fetchone()

    if nest is None:
        abort(404, "Nest id {0} doesn't exist.".format(nest_id))

    return nest

'''
Return a list of nests associated with a given apartment.
'''
def get_nests(apartment_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """SELECT *
        FROM nest
        WHERE apartment_id = %s""",
        (apartment_id,)
    )
    nests = cursor.fetchall()

    if nests is None:
        abort(404, "No nest associated with apartment id {0}.".format(apartment_id))

    return nests

'''
If a nest if full and all users in the nest has accepted offer, return true.
Otherwise false.
'''
def all_accept_offer(nest_id):
    if not is_nest_full:
        return False

    reservations = get_reservations(nest_id)
    for r in reservations:
        if r['accept_offer'] == 0:
            return False
    return True
    
