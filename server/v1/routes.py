from datetime import datetime, timedelta

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError

from server import bcrypt, db, Config
from server.config import CustomResponse, InvalidRequestException
from server.models import Customer, Card, Address, PhoneNumber

public_api = Blueprint('v1', __name__, url_prefix='/v1')


@public_api.route('/register/professor', methods=['POST'])
def register_professor():
    res = CustomResponse()
    try:
        password = Customer.generate_password()
        pw_hash = bcrypt.generate_password_hash(password=password)
        phone_numbers = request.json.get('phone_numbers')
        phone_numbers = list(
            map(lambda number: PhoneNumber(customer_ssn=request.json.get('ssn'), **number), phone_numbers))
        address = request.json.get('address')
        address = Address(**address)
        request.json['type'] = 'PROFESSOR'
        if phone_numbers is not None and address is not None:
            del request.json['phone_numbers']
            del request.json['address']
        else:
            raise InvalidRequestException('Address and phone numbers must not be empty!')
        cards = [Card(customer_ssn=request.json.get('ssn'), expiration_date=datetime.now() + timedelta(days=100000))]
        customer = Customer(**request.json, cards=cards, address=address, phone_numbers=phone_numbers, pw_hash=pw_hash)
        db.session.add(customer)
        db.session.commit()

        result = customer.get_relaxed_v1_view()
        result['password'] = password
        res.set_data(result)
        return res.get_response(201)
    except InvalidRequestException as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError as e:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    except:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()
