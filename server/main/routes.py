from flask import request, Blueprint, Response
from sqlalchemy.exc import IntegrityError
from server.config import CustomResponse, Config, InvalidRequestException, RecordNotFound
from server import db
from server.models import Campus, LibrarianWishlistItem

main = Blueprint('main', __name__, url_prefix='/api/library')


@main.route('/wishlist')
def fetch_library_wishlist() -> Response:
    res = CustomResponse()
    library_wishlist = db.session.query(LibrarianWishlistItem).all()
    res.set_data(list(map(lambda item: item.get_relaxed_view(), library_wishlist)))
    return res.get_response()


@main.route('/wishlist/add', methods=['PUT'])
def add_item_to_library_wishlist() -> Response:
    res = CustomResponse()
    try:
        item = LibrarianWishlistItem(**request.json)
        db.session.add(item)
        db.session.commit()
        res.set_data(item.get_relaxed_view())
    except InvalidRequestException as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError as e:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@main.route('/wishlist/remove/<id>', methods=['DELETE'])
def remove_item_from_library_wishlist(id: str) -> Response:
    res = CustomResponse()
    try:
        item = db.session.query(LibrarianWishlistItem).get(id)
        if item is None:
            raise RecordNotFound(id)
        db.session.delete(item)
        db.session.commit()
        res.set_data({'id': id})
    except RecordNotFound as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError as e:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@main.route('/static/campuses')
def fetch_campuses() -> Response:
    res = CustomResponse()
    campuses = db.session.query(Campus).all()
    res.set_data(list(map(lambda campus: campus.get_relaxed_view(), campuses)))
    return res.get_response()
