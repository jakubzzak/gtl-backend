from datetime import datetime
from flask import request, Blueprint, Response
from flask_login import login_required, current_user
from server.config import CustomResponse, InvalidRequestException, RecordNotFoundException
from server import db
from server.config import Config
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError
from server.models import Loan, Book

loans = Blueprint('loans', __name__, url_prefix='/api/loan')


@loans.route("/start", methods=['PUT'])
@login_required
def start_loan() -> Response:
    res = CustomResponse()
    try:
        if request.json['ssn'] is None or request.json['isbn'] is None:
            raise InvalidRequestException
        request.json['issued_by'] = current_user.ssn
        request.json['loaned_at'] = datetime.now()
        request.json['returned_at'] = None
        statement = text(f"""
            exec insertLoan
            @book_isbn = :isbn,
            @customer_ssn = :ssn,
            @issued_by = :issued_by,
            @loaned_at = :loaned_at,
            @returned_at = :returned_at
        """)
        db.session.execute(statement, request.json)
        db.session.commit()

        book = db.session.query(Book).get(request.json['isbn'])
        res.set_data(book.get_relaxed_view())
    except RecordNotFoundException or InvalidRequestException as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()


@loans.route("/close/<uuid:id>")
@login_required
def close_loan(id: str) -> Response:
    res = CustomResponse()
    try:
        loan = db.session.query(Loan).get(id)
        if loan is None:
            raise RecordNotFoundException(id)
        loan.close()
        db.session.commit()
    except RecordNotFoundException as e:
        db.session.rollback()
        res.set_error(e.message)
    except IntegrityError:
        db.session.rollback()
        res.set_error(Config.UNHANDLED_EXCEPTION_MESSAGE)
    return res.get_response()
