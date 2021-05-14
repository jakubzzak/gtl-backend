from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import registry
from sqlalchemy.ext.automap import automap_base
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from server.config import Config

db = SQLAlchemy()
# db_base = automap_base()
# db_base = registry()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'user_old.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    # with app.app_context():
        # db.create_all()
        # db_base.prepare(db.engine, reflect=True)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from server.search.routes import search
    from server.book.routes import books
    from server.customers.routes import customers
    from server.users.routes import users
    from server.main.routes import main

    app.register_blueprint(search)
    app.register_blueprint(books)
    app.register_blueprint(customers)
    app.register_blueprint(users)
    app.register_blueprint(main)

    return app
