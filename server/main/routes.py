from flask import request, Blueprint, Response
from sqlalchemy.exc import IntegrityError
from server.config import CustomResponse
from server import db
from server.models import Campus

main = Blueprint('main', __name__, url_prefix='/api/library')


@main.route('/wishlist/add', methods=['PUT'])
def add_item_to_library_wishlist() -> Response:
    res = CustomResponse()
    res.set_data(request.json)
    return res.get_response()


@main.route('/static/campuses')
def fetch_campuses() -> Response:
    res = CustomResponse()
    campuses = db.session.query(Campus).all()
    res.set_data(list(map(lambda campus: campus.get_relaxed_view(), campuses)))
    return res.get_response()
