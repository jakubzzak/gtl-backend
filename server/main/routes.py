from datetime import datetime, timedelta
from flask import request, session, Blueprint, Response
from sqlalchemy.exc import IntegrityError
from flask_login import login_required, current_user, login_user, logout_user
from server.config import CustomResponse, Config, InvalidRequestException, RecordNotFoundException, \
    UnauthorizedAccessException
from server import db, bcrypt
from server.models import Campus, LibrarianWishlistItem, Librarian, CustomerWishlistItem

main = Blueprint('main', __name__, url_prefix='/api/library')
main_unsecure = Blueprint('main_unsecure', __name__, url_prefix='/library')


@main_unsecure.route('/hash/<password>')
def translate_password(password: str) -> Response:
    res = CustomResponse()
    hash = Librarian.translate_password(password)
    res.set_data({
        'password': password,
        'hash': hash.decode("utf-8"),
    })
    return res.get_response()


@main_unsecure.route("/login", methods=['POST'])
def login() -> Response:
    res = CustomResponse()
    if current_user.is_authenticated:
        res.set_data(current_user.get_relaxed_view())
        return res.get_response()
    librarian = db.session.query(Librarian).filter(Librarian.email == request.json.get('email')).first()
    if librarian and bcrypt.check_password_hash(librarian.password, request.json.get('password')):
        login_user(librarian)
        session['login_type'] = 'librarian'
        res.set_data(librarian.get_relaxed_view())
    else:
        res.set_error('Wrong email or password!')
    return res.get_response()


@main.route("/logout")
@login_required
def logout() -> Response:
    res = CustomResponse(librarian_level=True)
    try:
        logout_user()
    except UnauthorizedAccessException as e:
        res.set_error(e.message)
        return res.get_response(status=401)
    except:
        res.set_error('Failed to log out user!')
    return res.get_response()


@main.route('/wishlist')
@login_required
def fetch_library_wishlist() -> Response:
    res = CustomResponse()
    library_wishlist = db.session.query(LibrarianWishlistItem).all()
    res.set_data(list(map(lambda item: item.get_relaxed_view(), library_wishlist)))
    return res.get_response()


@main.route('/wishlist/add', methods=['PUT'])
@login_required
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
@login_required
def remove_item_from_library_wishlist(id: str) -> Response:
    res = CustomResponse()
    try:
        item = db.session.query(LibrarianWishlistItem).get(id)
        if item is None:
            raise RecordNotFoundException(id)
        db.session.delete(item)
        db.session.commit()
        res.set_data({'id': id})
    except RecordNotFoundException as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError as e:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@main.route('/reservations')
@login_required
def fetch_library_reservations() -> Response:
    res = CustomResponse()
    library_reservations = db.session.query(CustomerWishlistItem) \
        .filter(CustomerWishlistItem.requested_at is not None,
                CustomerWishlistItem.requested_at > (datetime.now() - timedelta(days=30)),
                CustomerWishlistItem.picked_up == 0).all()
    res.set_data(list(map(lambda item: item.get_librarian_relaxed_view(), library_reservations)))
    return res.get_response()


@main_unsecure.route('/static/campuses')
def fetch_campuses() -> Response:
    res = CustomResponse()
    campuses = db.session.query(Campus).all()
    res.set_data(list(map(lambda campus: campus.get_relaxed_view(), campuses)))
    return res.get_response()
