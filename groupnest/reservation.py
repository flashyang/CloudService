from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from groupnest.auth import login_required
from groupnest.db import get_db

bp = Blueprint('reservation', __name__, url_prefix='/reservation')

@bp.route('/')
def index():
    return 'Hello, reservation!'