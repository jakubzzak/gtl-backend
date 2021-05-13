from flask import Blueprint, request, Response
from server.config import CustomResponse

customers = Blueprint('customers', __name__, url_prefix='/api/customer')


@customers.route('/<uuid:id>')
def get_customer(id: str) -> Response:
    res = CustomResponse()
    res.set_data({'id': id})
    return res.get_response()


@customers.route('/create', methods=['PUT'])
def create_new_customer() -> Response:
    res = CustomResponse()
    res.set_data(request.json)
    return res.get_response()


@customers.route('/<uuid:id>/update', methods=['POST'])
def update_customer(id: str) -> Response:
    res = CustomResponse()
    res.set_data({'id': id})
    return res.get_response()


@customers.route('/<uuid:id>/rentals/active')
def fetch_customers_active_rentals(id: str) -> Response:
    res = CustomResponse()
    res.set_data({'id': id})
    return res.get_response()


@customers.route('/<uuid:id>/card/extend')
def extend_customers_card_validity(id: str) -> Response:
    res = CustomResponse()
    res.set_data({'id': id})
    return res.get_response()
