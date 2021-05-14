from flask import request, Blueprint, Response
from server.config import CustomResponse, InvalidRequestException, RecordNotFound
from server import db
from server.models import Book


books = Blueprint('books', __name__, url_prefix='/api/book')


@books.route("/<isbn>")
def get_book(isbn: str) -> Response:
    res = CustomResponse(data=[])
    try:
        temp = db.session.query(Book).get(isbn)
        if temp is None:
            raise RecordNotFound(isbn)
        res.set_data(Book.jsonify(temp))
    except RecordNotFound as e:
        res.set_error(e.message)
    return res.get_response()


@books.route("/create", methods=['PUT'])
def create_book() -> Response:
    res = CustomResponse()
    res.set_data(request.json)
    return res.get_response()


@books.route("/<isbn>/update", methods=['POST'])
def update_book(isbn: str) -> Response:
    res = CustomResponse()
    res.set_data({'id': isbn})
    return res.get_response()


@books.route("/<isbn>/stock", methods=['POST'])
def update_book_stock(isbn: str) -> Response:
    res = CustomResponse()
    res.set_data({'id': isbn})
    return res.get_response()


@books.route("/<isbn>/disable", methods=['DELETE'])
def disable_book(isbn: str) -> Response:
    res = CustomResponse()
    res.set_data({'id': isbn})
    return res.get_response()
