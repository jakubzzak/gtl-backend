from flask import Blueprint, request, Response
from server import db
from sqlalchemy.exc import IntegrityError
from server.config import CustomResponse, RecordNotFound
from server.models import Customer, Card

customers = Blueprint('customers', __name__, url_prefix='/api/customer')


@customers.route('/find/<card_id>')
def find_customer(card_id: str) -> Response:
    res = CustomResponse(data=[])
    try:
        cards = db.session.query(Card).filter(Card.id.like(f"{card_id}%"))
        res.set_data(list(map(lambda card: card.get_search_view(), cards)))
    except IntegrityError as e:
        print(str(e))
    return res.get_response()


@customers.route('/<ssn>')
def get_customer(ssn: str) -> Response:
    res = CustomResponse(data=[])
    try:
        customer = db.session.query(Customer).get(ssn)
        if customer is None:
            raise RecordNotFound(ssn)
        res.set_data(customer.get_relaxed_view())
    except RecordNotFound as e:
        res.set_error(e.message)
    return res.get_response()


@customers.route('/create', methods=['PUT'])
def create_new_customer() -> Response:
    res = CustomResponse()
    res.set_data(request.json)
    return res.get_response()


@customers.route('/<ssn>/update', methods=['POST'])
def update_customer(ssn: str) -> Response:
    res = CustomResponse()
    res.set_data({'ssn': ssn})
    return res.get_response()


@customers.route('/<ssn>/rentals/active')
def fetch_customers_active_rentals(ssn: str) -> Response:
    res = CustomResponse()
    res.set_data({'ssn': ssn})
    return res.get_response()


@customers.route('/<ssn>/card/extend')
def extend_customers_card_validity(ssn: str) -> Response:
    res = CustomResponse()
    res.set_data({'ssn': ssn})
    return res.get_response()
