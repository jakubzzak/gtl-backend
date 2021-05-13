from flask import request, Blueprint, Response
from server.config import CustomResponse


main = Blueprint('main', __name__, url_prefix='/api/library')


@main.route('/wishlist/add', methods=['PUT'])
def add_item_to_library_wishlist() -> Response:
    res = CustomResponse()
    res.set_data(request.json)
    return res.get_response()
