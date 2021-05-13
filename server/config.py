import os
from flask import Response, json


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')


class CustomResponse:

    def __init__(self, data=None, error=None):
        self.ok = True
        self.data = data
        self.error = error

    def set_data(self, value: any) -> None:
        self.error = None
        self.data = value
        self.ok = True

    def set_error(self, value: str) -> None:
        self.data = None
        self.error = value
        self.ok = False

    def __repr__(self):
        return {'ok': self.ok, 'data': self.data, 'error': self.error}

    def get_response(self, status: int = None) -> Response:
        return Response(json.dumps({"ok": self.ok, "data": self.data, "error": self.error}),
                        status=status if status is not None else 200 if self.ok else 406, mimetype='application/json')
