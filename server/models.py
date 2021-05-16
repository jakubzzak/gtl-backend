from flask import current_app
from flask_login import UserMixin
from itsdangerous import Serializer
from datetime import datetime
from sqlalchemy import Table, Column, String, Text, Integer, Boolean, ForeignKey, SmallInteger, DateTime, Date
from sqlalchemy.orm import relationship, declarative_base
from server.config import InvalidRequestException


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
        Column('is_loanable', Boolean, default=True, nullable=False),
        Column('total_copies', Integer, nullable=False),
        Column('available_copies', Integer, nullable=False),
        Column('resource_type', String(30), nullable=False),
        Column('active', Boolean, default=True, nullable=False),
    )

    def __init__(self, isbn: str = None, title: str = None, author: str = None, subject_area: str = None,
                 description: str = None, is_loanable: bool = True, total_copies: int = 0,
                 available_copies: int = 0, resource_type: str = None, active: bool = True, **other):
        if len(other) > 0 or isbn is None or title is None or author is None \
                or subject_area is None or resource_type is None:
            raise InvalidRequestException

        self.isbn = isbn
        self.title = title
        self.author = author
        self.subject_area = subject_area
        self.description = description
        self.is_loanable = is_loanable
        self.total_copies = total_copies
        self.available_copies = available_copies
        self.resource_type = resource_type
        self.active = active

    def __repr__(self):
        return f"Book(title='{self.title}', author='{self.author}', area='{self.subject_area}', type='{self.resource_type}')"

    # @staticmethod
    # def jsonify(o: any) -> dict:
    #     temp = o.__dict__
    #     del temp['_sa_instance_state']
    #     return temp

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

    def update_record(self, title: str = None, author: str = None, subject_area: str = None,
                      description: str = None, is_loanable: bool = None, total_copies: int = None,
                      available_copies: int = None, resource_type: str = None, **other) -> dict:
        if len(other) > 0:
            raise InvalidRequestException

        if title is not None:
            self.title = title
        if author is not None:
            self.author = author
        if subject_area is not None:
            self.subject_area = subject_area
        if description is not None:
            self.description = description
        if is_loanable is not None:
            self.is_loanable = is_loanable
        if total_copies is not None:
            self.total_copies = total_copies
        if available_copies is not None:
            self.available_copies = available_copies
        if resource_type is not None:
            self.resource_type = resource_type

        return self.get_relaxed_view()

    def update_stock(self, total_copies: int = None, available_copies: int = None, **other) -> dict:
        if len(other) > 0:
            raise InvalidRequestException

        if total_copies is not None:
            self.total_copies = total_copies
        if available_copies is not None:
            self.available_copies = available_copies

        return self.get_relaxed_view()

    def remove_from_catalog(self) -> None:
        self.active = False


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

    def get_relaxed_view(self) -> dict:
        return {
            'id': self.id,
            'street': self.street,
            'number': self.number,
            'city': self.city,
            'post_code': self.post_code,
            'country': self.country
        }


class Campus(Base):
    __table__ = Table(
        'campus',
        Base.metadata,
        Column('address_id', Integer, ForeignKey('address.id'), primary_key=True),
    )

    address = relationship('Address')

    def __repr__(self):
        return f"Campus(address={self.address})"

    def get_relaxed_view(self) -> dict:
        return {
            'address': self.address.get_relaxed_view()
        }


class Customer(Base, UserMixin):
    __table__ = Table(
        'customer',
        Base.metadata,
        Column('ssn', String(20), primary_key=True),
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

    card = relationship('Card', lazy=True)
    campus = relationship('Campus', lazy=True)
    address = relationship('Address', lazy=True)
    wishlist_items = relationship('CustomerWishlistItem', lazy=True)
    phone_numbers = relationship('PhoneNumber', lazy=True)

    def __init__(self, ssn: str = None, email: str = None, pw_hash: str = None, first_name: str = None,
                 last_name: str = None, campus_id: int = None, type: str = 'STUDENT', home_address_id: int = None,
                 can_borrow: bool = True, can_reserve: bool = True, books_borrowed: int = 0, books_reserved: int = 0,
                 is_active: bool = True, **other):
        if len(other) > 0 or ssn is None or email is None or pw_hash is None \
                or first_name is None or last_name is None or campus_id is None or home_address_id is None:
            raise InvalidRequestException

        self.ssn = ssn
        self.email = email
        self.pw_hash = pw_hash
        self.first_name = first_name
        self.last_name = last_name
        self.campus_id = campus_id
        self.type = type
        self.home_address_id = home_address_id
        self.can_borrow = can_borrow
        self.can_reserve = can_reserve
        self.books_borrowed = books_borrowed
        self.books_reserved = books_reserved
        self.is_active = is_active

    def __repr__(self):
        return f"Customer({self.first_name} {self.last_name} ({self.email}), borrowed: {self.books_borrowed}, reserved: {self.books_reserved})"

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

    def get_relaxed_view(self) -> dict:
        return {
            'ssn': self.ssn,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'type': self.type,
            'card': list(filter(lambda card: card.is_active, self.card))[0].get_relaxed_view(),
            'campus': self.campus.get_relaxed_view(),
            'address': self.address.get_relaxed_view(),
            'phone_numbers': [phone_number.get_relaxed_view() for phone_number in self.phone_numbers],
            'wishlist': [wishlist_item.get_relaxed_view() for wishlist_item in self.wishlist_items],
            'can_borrow': self.can_borrow,
            'can_reserve': self.can_reserve,
            'is_active': self.is_active
        }


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

    def get_relaxed_view(self) -> dict:
        return {
            'id': self.id,
            'isbn': self.book_isbn,
            'requested_at': self.requested_at,
            'picked_up': self.picked_up,
        }


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

    def get_relaxed_view(self) -> dict:
        return {
            'country_code': self.country_code,
            'number': self.number,
            'type': self.type,
        }


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

    customer = relationship('Customer')

    def __repr__(self):
        return f"Card(ssn={self.customer_ssn} expires={self.expiration_date}, active={self.is_active})"

    def get_relaxed_view(self) -> dict:
        return {
            'id': self.id,
            'customer_ssn': self.customer_ssn,
            'expiration_date': self.expiration_date,
            'photo_path': self.photo_path,
        }

    def get_search_view(self):
        return {
            'card_id': self.id,
            'full_name': f"{self.customer.first_name} {self.customer.last_name}"
        }


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
