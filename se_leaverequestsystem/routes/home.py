from flask import (
    Blueprint
)
from SE_LeaveRequestSystem.se_leaverequestsystem.handlers import home

bp = Blueprint('home', __name__, url_prefix='/')


@bp.route('/', methods=['POST', 'GET', 'DELETE'])
def index():
    return home.index()