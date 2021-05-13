from flask import Blueprint, request

customers = Blueprint('customers', __name__)


@customers.route('/customers/<uuid:id>')
def get_customer(id: str):
    return request.args


@customers.route('/customers/create', methods=['PUT'])
def create_new_customer():
    return request.args


@customers.route('/customers/<uuid:id>/update', methods=['POST'])
def update_customer(id: str):
    return request.args


@customers.route('/customers/<uuid:id>/rentals/active')
def fetch_customers_active_rentals(id: str):
    return id


@customers.route('/customers/<uuid:id>/card/extend')
def extend_customers_card_validity(id: str):
    return id
