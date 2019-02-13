from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from groupnest.auth import login_required
from groupnest.db import get_db

bp = Blueprint('apartment', __name__, url_prefix='/apartment')

@bp.route('/')
def index():
    db = get_db()
    aprtments = db.execute(
        'SELECT top(10)*'
        'FROM db'
        'ORDER BY apartment_id DESC'
    ).fetchall()