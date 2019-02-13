from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from groupnest.auth import login_required
from groupnest.db import get_db

bp = Blueprint('apartment', __name__, url_prefix='/apartment')

@bp.route('/')
def index():
    return 'Hello, apartment!'