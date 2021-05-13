from flask import url_for, flash, redirect, request, Blueprint, Response
from flask_login import login_user, current_user, logout_user, login_required
from server.config import CustomResponse
from bcrypt import checkpw

users = Blueprint('users', __name__, url_prefix='/api/user')


@users.route("/login", methods=['POST'])
def login() -> Response:
    if current_user.is_authenticated:
        return redirect(url_for('main_old.home'))

    user = User.query.filter_by(email=request.json.email).first()
    if user and checkpw(user.password, request.json.password):
        login_user(user, remember=True)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main_old.home'))
    else:
        flash('Login Unsuccessful. Please check email and password', 'danger')



@users.route("/logout")
@login_required
def logout() -> Response:
    res = CustomResponse()
    logout_user()
    return res.get_response()
