from datetime import datetime, timedelta
from flask import Blueprint, request, Response
from server import db, bcrypt
from sqlalchemy.exc import IntegrityError
from server.config import CustomResponse, RecordNotFound, InvalidRequestException, Config
from server.models import Customer, Card, PhoneNumber, Address, Loan

customers = Blueprint('customers', __name__, url_prefix='/api/customer')


@customers.route('/find/<card_id>')
def find_customer(card_id: str) -> Response:
    res = CustomResponse(data=[])
    try:
        cards = db.session.query(Card).filter(Card.id.like(f"{card_id}%")).limit(10).all()
        res.set_data(list(map(lambda card: card.get_search_view(), cards)))
    except IntegrityError as e:
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
        # print(str(e))
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
    try:
        pw_hash = bcrypt.generate_password_hash(password=Customer.generate_password())
        phone_numbers = list(map(lambda number: PhoneNumber(customer_ssn=request.json['ssn'], **number), request.json['phone_numbers']))
        del request.json['phone_numbers']
        address = Address(**request.json['address'])
        del request.json['address']
        cards = [Card(customer_ssn=request.json['ssn'], expiration_date=datetime.now() + timedelta(days=365 * 4))]
        customer = Customer(**request.json, cards=cards, address=address, phone_numbers=phone_numbers, pw_hash=pw_hash)
        db.session.add(customer)
        db.session.commit()
        res.set_data(customer.get_relaxed_view())
        return res.get_response(201)
    except IntegrityError as e:
        db.session.rollback()
        # print('exception occurred', e)
        res.set_error(f"Item you are trying to add already exists!")
    except InvalidRequestException as e:
        db.session.rollback()
        res.set_error(e.message)
    return res.get_response()


@customers.route('/<ssn>/update', methods=['POST'])
def update_customer(ssn: str) -> Response:
    res = CustomResponse()
    try:
        customer = db.session.query(Customer).get(ssn)
        if customer is None:
            raise RecordNotFound()
        customer.update_record(**request.json)
        db.session.commit()
        res.set_data(customer.get_relaxed_view())
    except InvalidRequestException or RecordNotFound as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError as e:
        db.session.rollback()
        print('exception occurred', e)
        res.set_error(f"Item you are trying to add already exists!")
    return res.get_response()


@customers.route('/<ssn>/disable', methods=['DELETE'])
def disable_customer(ssn: str) -> Response:
    res = CustomResponse()
    try:
        customer = db.session.query(Customer).get(ssn)
        if customer is None or not customer.is_active:
            raise RecordNotFound()
        customer.disable_record()
        db.session.commit()
        res.set_data(customer.get_relaxed_view())
    except InvalidRequestException or RecordNotFound as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError as e:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@customers.route('/<ssn>/enable')
def enable_customer(ssn: str) -> Response:
    res = CustomResponse()
    try:
        customer = db.session.query(Customer).get(ssn)
        if customer is None or customer.is_active:
            raise RecordNotFound()
        customer.enable_record()
        db.session.commit()
        res.set_data(customer.get_relaxed_view())
    except InvalidRequestException or RecordNotFound as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError as e:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@customers.route('/<ssn>/rentals/active')
def fetch_customers_active_rentals(ssn: str) -> Response:
    res = CustomResponse(data=[])
    try:
        active_loans = db.session.query(Loan).filter(Loan.customer_ssn == ssn, Loan.returned_at is None).all()
        res.set_data(list(map(lambda loan: loan.get_relaxed_view(), active_loans)))
    except IntegrityError as e:
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
        # print(str(e))
    return res.get_response()


@customers.route('/card/<id>/extend')
def extend_customers_card_validity(id: str) -> Response:
    res = CustomResponse()
    try:
        card = db.session.query(Card).get(id)
        if card is None or card.customer.is_active is False:
            raise RecordNotFound(id)
        card.extend_validity()
        db.session.commit()
        res.set_data(card.customer.get_relaxed_view())
    except RecordNotFound as e:
        db.session.rollback()
        res.set_error(e.message)

    return res.get_response()
