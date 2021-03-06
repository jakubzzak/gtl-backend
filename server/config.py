from dotenv import load_dotenv
import os
from flask import Response, json, session

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    UNHANDLED_EXCEPTION_MESSAGE = os.environ.get('UNHANDLED_EXCEPTION_MESSAGE') \
        if os.environ.get('UNHANDLED_EXCEPTION_MESSAGE') is not None \
        else 'Ups! Unhandled exception occurred.'


class UnauthorizedAccessException(Exception):

    def __init__(self, message: str = None):
        self.message = message if message is not None else 'Unauthorized access!'


class InvalidRequestException(Exception):

    def __init__(self, message: str = 'Invalid request!'):
        self.message = message


class RecordAlreadyExistsException(Exception):

    def __init__(self, value: str = None):
        self.message = f"Record with value {value} already exist!" if value is not None else f"Record already exist!"


class RecordNotFoundException(Exception):

    def __init__(self, value: str = None):
        self.message = f"Record with value {value} does not exist!" if value is not None else f"Record does not exist!"


class CustomResponse:

    def __init__(self, data: any = None, error: str = None, librarian_level: bool = False):
        if librarian_level and session.get('login_type') != 'librarian':
            self.ok = False
            self.data = None
            self.error = None
            raise UnauthorizedAccessException

        self.ok = True
        self.data = data
        self.error = error

    def get_data(self):
        return self.data

    def set_data(self, value: any) -> None:
        self.error = None
        self.data = value
        self.ok = True

    def set_error(self, value: str) -> None:
        self.data = None
        self.error = value
        self.ok = False

    def __repr__(self):
        return f"CustomResponse(ok={self.ok} data={self.data}, error={self.error})"

    def get_response(self, status: int = None) -> Response:
        return Response(json.dumps({"ok": self.ok, "data": self.data, "error": self.error}),
                        status=status if status is not None else 200 if self.ok else 406, mimetype='application/json')
