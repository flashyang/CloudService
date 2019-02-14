from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from groupnest.auth import login_required
from groupnest.db import get_db

bp = Blueprint('reservation', __name__, url_prefix='/reservation')

@bp.route('/nest_id/<int:nest_id>/create', methods=('GET', 'POST'))
@login_required
def create(nest_id):
    if request.method == 'POST':
        db = get_db()
        db.execute(
            'INSERT INTO reservation (nest_id, tenant_id)'
            ' VALUES (?, ?)',
            (nest_id, g.user['user_id'])
        )
        db.commit()
    return redirect(url_for('nest.index', nest_id))


