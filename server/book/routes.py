from flask import request, Blueprint, Response
from server.config import CustomResponse, InvalidRequestException, RecordNotFound
from server import db
from server.config import Config
from sqlalchemy.exc import IntegrityError
from server.models import Book


books = Blueprint('books', __name__, url_prefix='/api/book')


@books.route('/find/<isbn>')
def find_customer(isbn: str) -> Response:
    res = CustomResponse(data=[])
    try:
        _books = db.session.query(Book).filter(Book.isbn.like(f"{isbn}%"), Book.deleted == 0).limit(10).all()
        res.set_data(list(map(lambda book: book.get_search_view(), _books)))
    except IntegrityError as e:
        print(str(e))
    return res.get_response()


@books.route("/<isbn>")
def get_book(isbn: str) -> Response:
    res = CustomResponse(data=[])
    try:
        book = db.session.query(Book).get(isbn)
        if book is None or book.deleted:
            raise RecordNotFound(isbn)
        res.set_data(book.get_relaxed_view())
    except RecordNotFound as e:
        res.set_error(e.message)
    return res.get_response()


@books.route("/create", methods=['PUT'])
def create_book() -> Response:
    res = CustomResponse()
    try:
        book = Book(**request.json)
        db.session.add(book)
        db.session.commit()
        res.set_data(book.get_relaxed_view())
        return res.get_response(201)
    except IntegrityError:
        db.session.rollback()
        res.set_error(f"Item you are trying to add already exists!")
    except InvalidRequestException as e:
        db.session.rollback()
        res.set_error(e.message)
    return res.get_response()


@books.route("/<isbn>/update", methods=['POST'])
def update_book(isbn: str) -> Response:
    res = CustomResponse()
    try:
        book = db.session.query(Book).get(isbn)
        if book is None or book.deleted:
            raise RecordNotFound(isbn)
        book.update_record(**request.json)
        db.session.commit()
        res.set_data(book.get_relaxed_view())
    except InvalidRequestException or RecordNotFound as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError as e:
        print(e)
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@books.route("/<isbn>/stock", methods=['POST'])
def update_book_stock(isbn: str) -> Response:
    res = CustomResponse()
    try:
        book = db.session.query(Book).get(isbn)
        if book is None or book.deleted:
            raise RecordNotFound(isbn)
        book.update_stock(**request.json)
        db.session.commit()
        res.set_data(book.get_relaxed_view())
    except InvalidRequestException or RecordNotFound as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@books.route("/<isbn>/disable", methods=['DELETE'])
def disable_book(isbn: str) -> Response:
    res = CustomResponse()
    try:
        book = db.session.query(Book).get(isbn)
        if book is None or not book.deleted:
            raise RecordNotFound(isbn)
        book.disable_record()
        db.session.commit()
        res.set_data(book.get_relaxed_view())
    except RecordNotFound as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@books.route("/<isbn>/enable")
def enable_book(isbn: str) -> Response:
    res = CustomResponse()
    try:
        book = db.session.query(Book).get(isbn)
        if book is None or book.deleted:
            raise RecordNotFound(isbn)
        book.enable_record()
        db.session.commit()
        res.set_data(book.get_relaxed_view())
    except RecordNotFound as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()
