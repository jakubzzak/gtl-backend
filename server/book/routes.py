from flask import request, Blueprint, Response
from server.config import CustomResponse

books = Blueprint('books', __name__, url_prefix='/api/book')


@books.route("/<uuid:id>")
def get_book(id: str) -> Response:
    res = CustomResponse()
    res.set_data({'id': id})
    return res.get_response()


@books.route("/create", methods=['PUT'])
def create_book() -> Response:
    res = CustomResponse()
    res.set_data(request.json)
    return res.get_response()


@books.route("/<uuid:id>/update", methods=['POST'])
def update_book(id: str) -> Response:
    res = CustomResponse()
    res.set_data({'id': id})
    return res.get_response()


@books.route("/<uuid:id>/stock", methods=['POST'])
def update_book_stock(id: str) -> Response:
    res = CustomResponse()
    res.set_data({'id': id})
    return res.get_response()


@books.route("/<uuid:id>/disable", methods=['DELETE'])
def disable_book(id: str) -> Response:
    res = CustomResponse()
    res.set_data({'id': id})
    return res.get_response()
