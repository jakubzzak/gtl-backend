from datetime import datetime, timedelta

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text

from server import bcrypt, db, Config
from server.config import CustomResponse, InvalidRequestException
from server.models import Customer, Card, Address, PhoneNumber

public_api = Blueprint('v1', __name__, url_prefix='/v1')


@public_api.route('/register/professor', methods=['PUT'])
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


@public_api.route('/statistics/books/popular/<int:count>')
def fetch_top_x_popular_books(count: int):
    res = CustomResponse()
    try:
        with db.engine.connect() as con:
            statement = text(f"""exec fetch_top_x_popular_books @limit = :count;""")
            rs = con.execute(statement, {'count': count})
            data = []
            for row in rs:
                data.append(dict(row))
            res.set_data(data)
    except Exception as e:
        print(str(e))
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@public_api.route('/statistics/loans/averageTimeInDays')
def get_average_loan_time_in_days():
    res = CustomResponse()
    try:
        with db.engine.connect() as con:
            rs = con.execute("exec get_average_loan_time_in_days;")
            data = []
            for row in rs:
                data.append({'days': row['average_loan_length_in_days']})
            res.set_data(data)
    except:
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()
