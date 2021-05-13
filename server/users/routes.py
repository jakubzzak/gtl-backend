from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from bcrypt import checkpw

users = Blueprint('users', __name__)


@users.route("/users/login", methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_old.home'))

    user = User.query.filter_by(email=request.json.email).first()
    if user and checkpw(user.password, request.json.password):
        login_user(user, remember=True)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main_old.home'))
    else:
        flash('Login Unsuccessful. Please check email and password', 'danger')



@users.route("/users/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_old.home'))
