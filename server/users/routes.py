from flask import request, session, Blueprint, Response
from flask_login import login_user, current_user, logout_user, login_required
from server.config import CustomResponse, RecordAlreadyExistsException, RecordNotFoundException
from server import db, bcrypt, Config
from server.models import Customer, Loan, CustomerWishlistItem

users = Blueprint('users', __name__, url_prefix='/api/user')
users_unsecure = Blueprint('users_unsecure', __name__, url_prefix='/user')


# @users_unsecure.route('/hash/<password>')
def translate_password(password: str) -> Response:
    res = CustomResponse()
    hash = Customer.translate_password(password)
    res.set_data({
        'password': password,
        'hash': hash.decode("utf-8"),
    })
    return res.get_response()


@users_unsecure.route("/login", methods=['POST'])
def login() -> Response:
    res = CustomResponse()
    if current_user.is_authenticated:
        res.set_data(current_user.get_relaxed_view())
        return res.get_response()
    user = db.session.query(Customer).filter(Customer.email == request.json.get('email')).first()
    if user and bcrypt.check_password_hash(user.password, request.json.get('password')):
        login_user(user)
        session['login_type'] = 'customer'
        res.set_data(user.get_relaxed_view())
    else:
        res.set_error('Wrong email or password!')
    return res.get_response()


@users.route("/logout")
@login_required
def logout() -> Response:
    res = CustomResponse()
    logout_user()
    return res.get_response()


@users.route('/history')
@login_required
def fetch_history() -> Response:
    res = CustomResponse()
    if current_user is None or current_user.ssn is None:
        logout_user()
        return res.get_response()
    loans = db.session.query(Loan).filter(Loan.customer_ssn == current_user.ssn).order_by(Loan.loaned_at.desc()).all()
    res.set_data(list(map(lambda loan: loan.get_relaxed_view(), loans)))
    return res.get_response()


@users.route('/wishlist')
@login_required
def fetch_wishlist() -> Response:
    res = CustomResponse()
    if current_user is None:
        logout_user()
        return res.get_response()
    try:
        res.set_data(list(map(lambda item: item.get_relaxed_view(), current_user.wishlist_items)))
    except:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@users.route('/wishlist/add/<isbn>', methods=['PUT'])
@login_required
def add_to_wishlist(isbn: str) -> Response:
    res = CustomResponse()
    if current_user is None:
        logout_user()
        return res.get_response()
    try:
        if isbn in list(map(lambda item: item.book_isbn, current_user.wishlist_items)):
            raise RecordAlreadyExistsException(isbn)
        current_user.wishlist_items.append(CustomerWishlistItem(book_isbn=isbn, customer_ssn=current_user.ssn))
        db.session.commit()
        res.set_data(list(map(lambda item: item.get_relaxed_view(), current_user.wishlist_items)))
    except RecordAlreadyExistsException as e:
        db.session.rollback()
        res.set_error(e.message)
    except:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@users.route('/wishlist/remove/<isbn>', methods=['DELETE'])
@login_required
def remove_from_wishlist(isbn: str) -> Response:
    res = CustomResponse()
    if current_user is None:
        logout_user()
        return res.get_response()
    try:
        if isbn not in list(map(lambda item: item.book_isbn, current_user.wishlist_items)):
            raise RecordNotFoundException(isbn)
        db.session.delete(list(filter(lambda item: item.book_isbn == isbn, current_user.wishlist_items))[0])
        db.session.commit()
        res.set_data(list(map(lambda item: item.get_relaxed_view(), current_user.wishlist_items)))
    except RecordNotFoundException as e:
        db.session.rollback()
        res.set_error(e.message)
    except:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@users.route('/wishlist/request/<id>')
@login_required
def request_from_wishlist(id: str) -> Response:
    res = CustomResponse()
    if current_user is None:
        logout_user()
        return res.get_response()
    try:
        if id not in list(map(lambda item: item.id, current_user.wishlist_items)):
            raise RecordNotFoundException(id)
        wishlist_item = list(filter(lambda item: item.id == id, current_user.wishlist_items))[0]
        wishlist_item.request_now()
        db.session.commit()
        res.set_data(list(map(lambda item: item.get_relaxed_view(), current_user.wishlist_items)))
    except RecordNotFoundException as e:
        db.session.rollback()
        res.set_error(e.message)
    except:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()
