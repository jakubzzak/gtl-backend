from flask import current_app
from flask_login import UserMixin
from itsdangerous import Serializer
from datetime import datetime
from sqlalchemy import Table, Column, String, Text, Integer, Boolean, ForeignKey, SmallInteger, DateTime, Date
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()


class Book(Base):
    __table__ = Table(
        'book',
        Base.metadata,
        Column('isbn', String(30), primary_key=True),
        Column('title', String(150), nullable=False),
        Column('author', String(100), nullable=False),
        Column('subject_area', String(100), nullable=False),
        Column('description', Text),
        Column('is_loanable', Boolean, nullable=False, default=True),
        Column('total_copies', Integer, nullable=False),
        Column('available_copies', Integer, nullable=False),
        Column('resource_type', String(30), nullable=False),
    )

    def __init__(self, isbn: str, title: str, author: str, subject_area: str, description: str, is_loanable: bool,
                 total_copies: int, available_copies: int, resource_type: str):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.subject_area = subject_area
        self.description = description
        self.is_loanable = is_loanable
        self.total_copies = total_copies
        self.available_copies = available_copies
        self.resource_type = resource_type

    @staticmethod
    def jsonify(o: any) -> dict:
        temp = o.__dict__
        del temp['_sa_instance_state']
        return temp

    def get_relaxed_view(self) -> dict:
        return {
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'subject_area': self.subject_area,
            'description': self.description,
            'available_copies': self.available_copies,
            'is_loanable': self.is_loanable
        }

    def __repr__(self):
        return f"Book(title='{self.title}', author='{self.author}', area='{self.subject_area}', type='{self.resource_type}')"


class Address(Base):
    __table__ = Table(
        'address',
        Base.metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('street', String(150)),
        Column('number', String(50)),
        Column('city', String(100), nullable=False),
        Column('post_code', String(20), nullable=False),
        Column('country', String(100), nullable=False),
    )

    def __repr__(self):
        return f"Address({self.street} {self.author}, {self.post_code} {self.city}, {self.country})"


class Campus(Base):
    __table__ = Table(
        'campus',
        Base.metadata,
        Column('address_id', Integer, ForeignKey('address.id'), primary_key=True),
    )

    address = relationship('Address')

    def __repr__(self):
        return f"Campus(address={self.address})"


class Customer(Base, UserMixin):
    __table__ = Table(
        'customer',
        Base.metadata,
        Column('id', String, primary_key=True),
        Column('ssn', String(20), nullable=False, unique=True),
        Column('email', String(100), nullable=False, unique=True),
        Column('password', String(60), nullable=False),
        Column('first_name', String(100), nullable=False),
        Column('last_name', String(100), nullable=False),
        Column('campus_id', Integer, ForeignKey('campus.address_id'), nullable=False),
        Column('type', String(20), nullable=False),
        Column('home_address_id', Integer, ForeignKey('address.id')),
        Column('can_reserve', Boolean, default=True, nullable=False),
        Column('can_borrow', Boolean, default=True, nullable=False),
        Column('books_borrowed', SmallInteger, default=0, nullable=False),
        Column('books_reserved', SmallInteger, default=0, nullable=False),
        Column('is_active', Boolean, default=True, nullable=False),
    )

    wishlist_items = relationship('CustomerWishlistItem', lazy=True)
    phone_numbers = relationship('PhoneNumber', lazy=True)

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['CUSTOMER_SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Customer.query.get(user_id)

    def get_reset_token(self, expires_sec=3600):
        s = Serializer(current_app.config['CUSTOMER_SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def __repr__(self):
        return f"Customer({self.first_name} {self.last_name} ({self.email}), borrowed: {self.books_borrowed}, reserved: {self.books_reserved})"


class CustomerWishlistItem(Base):
    __table__ = Table(
        'customer_wishlist_item',
        Base.metadata,
        Column('id', String, primary_key=True),
        Column('customer_ssn', String, ForeignKey('customer.ssn'), nullable=False),
        Column('book_isbn', String, ForeignKey('book.isbn'), nullable=False),
        Column('requested_at', DateTime),
        Column('picked_up', Boolean, default=False, nullable=False),
    )

    def __repr__(self):
        return f"Customer wishlist item(customer={self.customer_ssn}, book={self.book_isbn}, requested_at={self.requested_at}, picked_up={self.picked_up})"


class PhoneNumber(Base):
    __table__ = Table(
        'phone_number',
        Base.metadata,
        Column('customer_ssn', String, ForeignKey('customer.ssn'), primary_key=True),
        Column('country_code', String(5), primary_key=True),
        Column('number', String(15), primary_key=True),
        Column('type', String(30), nullable=False),
    )

    def __repr__(self):
        return f"Phone number(+{self.country_code} {self.number}, {self.type})"


class Card(Base):
    __table__ = Table(
        'card',
        Base.metadata,
        Column('id', String, primary_key=True),
        Column('customer_ssn', String, ForeignKey('customer.ssn'), nullable=False),
        Column('expiration_date', Date, nullable=False),
        Column('photo_path', String(150), nullable=False),
        Column('is_active', Boolean, default=True, nullable=False),
    )

    def __repr__(self):
        return f"Card({self.country_code} {self.number}, {self.type})"


class Librarian(Base, UserMixin):
    __table__ = Table(
        'librarian',
        Base.metadata,
        Column('id', String, primary_key=True),
        Column('ssn', String(20), nullable=False, unique=True),
        Column('email', String(100), nullable=False, unique=True),
        Column('password', String(60), nullable=False),
        Column('first_name', String(100), nullable=False),
        Column('last_name', String(100), nullable=False),
        Column('position', String(30), nullable=False),
    )

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Librarian.query.get(user_id)

    def get_reset_token(self, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def __repr__(self):
        return f"Librarian({self.first_name} {self.last_name} ({self.email}), {self.position})"


class LibrarianWishlistItem(Base):
    __table__ = Table(
        'librarian_wishlist_item',
        Base.metadata,
        Column('id', String, primary_key=True),
        Column('title', String(100), nullable=False),
        Column('description', Text),
    )

    def __repr__(self):
        return f"Librarian wishlist item(title={self.title}, description={self.description})"


class Loan(Base):
    __table__ = Table(
        'loan',
        Base.metadata,
        Column('id', String, primary_key=True),
        Column('book_isbn', String(30), ForeignKey('book.isbn'), nullable=False),
        Column('customer_ssn', String(20), ForeignKey('customer.ssn'), nullable=False, index=True),
        Column('issued_by', String, ForeignKey('librarian.ssn'), nullable=False),
        Column('loaned_at', DateTime, default=datetime.utcnow, nullable=False, index=True),
        Column('returned_at', DateTime),
    )

    book = relationship('Book', lazy=True)
    customer = relationship('Customer', lazy=True)
    librarian = relationship('Librarian', lazy=True)

    def __repr__(self):
        return f"Loan(book='{self.book_isbn}' customer='{self.customer_ssn}' ({self.loaned_at} - {self.returned_at})"
