from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from sqlalchemy import Column, String, Text, SmallInteger, Integer, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from server import db, db_base, login_manager
from flask_login import UserMixin


Base = declarative_base()

# class UserModel(db.Model, UserMixin):
#     id = Column(Integer, primary_key=True)
#     username = Column(String(20), unique=True, nullable=False)
#     email = Column(String(120), unique=True, nullable=False)
#     image_file = Column(String(20), nullable=False, default='default.jpg')
#     password = Column(String(60), nullable=False)
#     posts = relationship('Post', backref='author', lazy=True)
#
#     def __repr__(self):
#         return f"User('{self.username}', '{self.email}', '{self.image_file}')"
#
#
# class Post(db.Model):
#     id = Column(Integer, primary_key=True)
#     title = Column(String(100), nullable=False)
#     date_posted = Column(DateTime, nullable=False, default=datetime.utcnow)
#     content = Column(Text, nullable=False)
#     user_id = Column(Integer, ForeignKey('user_old.id'), nullable=False)
#
#     def __repr__(self):
#         return f"Post('{self.title}', '{self.date_posted}')"


class Address(db_base):
    __tablename__ = 'address'
    # __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    street = Column(String(150))
    number = Column(String(50))
    city = Column(String(100), nullable=False)
    post_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)

    campus = relationship('Campus')

    def __repr__(self):
        return f"Address({self.street} {self.author}, {self.post_code} {self.city}, {self.country})"


class Campus(db_base):
    __tablename__ = 'campus'
    __table_args__ = {'extend_existing': True}

    address_id = Column(Integer, ForeignKey('address.id'), primary_key=True)
    # address = relationship('Address', backref='id', lazy=True)

    def __repr__(self):
        return f"Address({self.street} {self.author}, {self.post_code} {self.city}', {self.country}')"


class CustomerModel(db.Model, UserMixin):
    id = Column(String, primary_key=True)
    ssn = Column(String(20), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(60), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    campus_id = Column(Integer, ForeignKey('campus.address_id'), nullable=False)
    type = Column(String(20), nullable=False)
    home_address_id = Column(Integer, ForeignKey('address.id'))
    can_reserve = Column(Boolean, default=True, nullable=False)
    can_borrow = Column(Boolean, default=True, nullable=False)
    books_borrowed = Column(SmallInteger, default=0, nullable=False)
    books_reserved = Column(SmallInteger, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['CUSTOMER_SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return CustomerModel.query.get(user_id)

    def get_reset_token(self, expires_sec=3600):
        s = Serializer(current_app.config['CUSTOMER_SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def __repr__(self):
        return f"Customer({self.first_name} {self.last_name} ({self.email}), borrowed: {self.books_borrowed}, reserved: {self.books_reserved})"


class CustomerWishlistItemModel(db.Model):
    id = Column(String, primary_key=True)
    customer_ssn = Column(String, ForeignKey('customer.ssn'), nullable=False)
    book_isbn = Column(String, ForeignKey('book.isbn'), nullable=False)
    requested_at = Column(DateTime)
    picked_up = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"Customer wishlist item(customer={self.customer_ssn}, book={self.book_isbn}, requested_at={self.requested_at}, picked_up={self.picked_up})"


class Book(db_base):
    __tablename__ = 'book'
    __table_args__ = {'extend_existing': True}

    isbn = Column(String(30), primary_key=True)
    title = Column(String(150), nullable=False)
    author = Column(String(100), nullable=False)
    subject_area = Column(String(100), nullable=False)
    description = Column(Text)
    is_loanable = Column(Boolean, nullable=False, default=True)
    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, nullable=False)
    resource_type = Column(String(30), nullable=False)

    def __repr__(self):
        return f"Book(title='{self.title}', author='{self.author}', area='{self.subject_area}', type='{self.resource_type}')"


class LibrarianModel(db.Model, UserMixin):
    id = Column(String, primary_key=True)
    ssn = Column(String(20), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(60), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    position = Column(String(30), nullable=False)

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return LibrarianModel.query.get(user_id)

    def get_reset_token(self, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def __repr__(self):
        return f"Librarian({self.first_name} {self.last_name} ({self.email}), {self.position})"


class LibrarianWishlistItemModel(db.Model):
    id = Column(String, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)

    def __repr__(self):
        return f"Librarian wishlist item(title={self.title}, description={self.description})"


class PhoneNumberModel(db.Model):
    customer_ssn = Column(String, ForeignKey('customer.ssn'), primary_key=True)
    country_code = Column(String(5), primary_key=True)
    number = Column(String(15), primary_key=True)
    type = Column(String(30), nullable=False)

    def __repr__(self):
        return f"Phone number(+{self.country_code} {self.number}, {self.type})"


class CardModel(db.Model):
    id = Column(String, primary_key=True)
    customer_ssn = Column(String, ForeignKey('customer.ssn'), nullable=False)
    expiration_date = Column(Date, nullable=False)
    photo_path = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"Card({self.country_code} {self.number}, {self.type})"


class Loan(db.Model):
    id = Column(String, primary_key=True)
    book_isbn = Column(String(30), ForeignKey('book.isbn'), nullable=False)
    customer_ssn = Column(String(20), ForeignKey('customer.ssn'), nullable=False, index=True)
    issued_by = Column(String, ForeignKey('librarian.ssn'), nullable=False)
    loaned_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    returned_at = Column(DateTime)

    def __repr__(self):
        return f"Loan(book='{self.book_isbn}' customer='{self.customer_ssn}' ({self.loaned_at} - {self.returned_at})"


@login_manager.user_loader
def load_customer(user_id: int) -> CustomerModel:
    return CustomerModel.query.get(int(user_id))


db_base.prepare()
