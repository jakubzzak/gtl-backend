from flask import request, Blueprint

book = Blueprint('book', __name__)


@book.route("/book/<uuid:id>")
def get_book(id: str):
    return id


@book.route("/book/create", methods=['PUT'])
def create_book():
    return request.json


@book.route("/book/<uuid:id>/update", methods=['POST'])
def update_book(id: str):
    return request.json


@book.route("/book/<uuid:id>/stock", methods=['POST'])
def update_book_stock(id: str):
    return request.json


@book.route("/book/<uuid:id>/disable", methods=['DELETE'])
def disable_book(id: str):
    return id
