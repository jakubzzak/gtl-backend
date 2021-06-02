from flask import current_app, session
from datetime import datetime, timedelta
from flask_login import UserMixin
from itsdangerous import Serializer
from sqlalchemy import Table, Column, String, Text, Integer, Boolean, ForeignKey, SmallInteger, DateTime, Date, \
    FetchedValue
from sqlalchemy.orm import relationship, declarative_base
from server.config import InvalidRequestException
from string import ascii_letters, digits
from random import choice, randint
from server import db, login_manager, bcrypt

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
        Column('deleted', Boolean, default=False, nullable=False),
    )

    def __init__(self, isbn: str = None, title: str = None, author: str = None, subject_area: str = None,
                 description: str = None, is_loanable: bool = True, total_copies: int = 0,
                 available_copies: int = 0, resource_type: str = 'BOOK', deleted: bool = False, **other: dict):
        if len(other) > 0 or isbn is None or title is None or author is None or subject_area is None:
            raise InvalidRequestException

        self.isbn = isbn
        self.title = title
        self.author = author
        self.subject_area = subject_area
        self.description = description
        self.total_copies = total_copies
        self.available_copies = available_copies
        self.resource_type = resource_type
        self.is_loanable = is_loanable
        self.deleted = deleted

    def __repr__(self):
        return f"Book(title='{self.title}', author='{self.author}', area='{self.subject_area}', " \
               f"type='{self.resource_type}', {'was deleted' if self.deleted else ''})"

    def get_relaxed_view(self) -> dict:
        return {
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'subject_area': self.subject_area,
            'description': self.description,
            'resource_type': self.resource_type,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'is_loanable': self.is_loanable,
            'is_active': not self.deleted,
        }

    def get_search_view(self):
        return {
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
        }

    def update_record(self, title: str = None, author: str = None, subject_area: str = None,
                      description: str = None, is_loanable: bool = None, resource_type: str = None,
                      **other: dict) -> dict:
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
        if resource_type is not None:
            self.resource_type = resource_type

        return self.get_relaxed_view()

    def update_stock(self, total_copies: int = None, available_copies: int = None, **other: dict) -> dict:
        if len(other) > 0:
            raise InvalidRequestException

        if total_copies is not None:
            self.total_copies = total_copies
        if available_copies is not None:
            self.available_copies = available_copies

        return self.get_relaxed_view()

    def disable_record(self) -> None:
        self.deleted = True

    def enable_record(self) -> None:
        self.deleted = False


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

    def __init__(self, street: str = None, number: str = None, city: str = None,
                 post_code: str = None, country: str = None, **other: dict):
        if len(other) > 0 or city is None or post_code is None or country is None:
            raise InvalidRequestException

        self.street = street
        self.number = number
        self.city = city
        self.post_code = post_code
        self.country = country

    def __repr__(self):
        return f"Address({self.street} {self.number}, {self.post_code} {self.city}, {self.country})"

    def update_record(self, street: str = None, number: str = None, city: str = None,
                      post_code: str = None, country: str = None, **other: dict):
        if len(other) > 0:
            raise InvalidRequestException

        if street is not None:
            self.street = street
        if number is not None:
            self.number = number
        if city is not None:
            self.city = city
        if post_code is not None:
            self.post_code = post_code
        if country is not None:
            self.country = country

        return self.get_relaxed_view()

    def get_relaxed_view(self) -> dict:
        return {
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

    def __init__(self, address: Address = None, **other: dict):
        if len(other) > 0 or address is None:
            raise InvalidRequestException

        self.address = address

    def __repr__(self):
        return f"Campus(address={self.address})"

    def get_relaxed_view(self) -> dict:
        return {
            'id': self.address_id,
            'address': self.address.get_relaxed_view()
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

    def __init__(self, customer_ssn: str = None, country_code: str = None,
                 number: str = None, type: str = 'HOME', **other: dict):
        if len(other) > 0 or customer_ssn is None or country_code is None or number is None:
            raise InvalidRequestException

        self.customer_ssn = customer_ssn
        self.country_code = country_code
        self.number = number
        self.type = type

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
        Column('id', String, primary_key=True, server_default=FetchedValue()),
        Column('customer_ssn', String, ForeignKey('customer.ssn'), nullable=False),
        Column('expiration_date', Date, nullable=False),
        Column('photo_path', String(150), nullable=False),
        Column('is_active', Boolean, default=True, nullable=False),
    )

    customer = relationship('Customer')

    def __init__(self, customer_ssn: str = None, expiration_date: datetime = None,
                 photo_path: str = 'default.png', is_active: bool = True, **other: dict):
        if len(other) > 0 or customer_ssn is None or expiration_date is None:
            raise InvalidRequestException

        self.customer_ssn = customer_ssn
        self.expiration_date = expiration_date
        self.photo_path = photo_path
        self.is_active = is_active

    def __repr__(self):
        return f"Card(ssn={self.customer_ssn} expires={self.expiration_date}, active={self.is_active})"

    def extend_validity(self):
        self.expiration_date = datetime.now() + timedelta(days=365)

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
            'ssn': self.customer_ssn,
            'city': self.customer.address.city,
            'full_name': f"{self.customer.first_name} {self.customer.last_name}"
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

    cards = relationship('Card', lazy=True)
    campus = relationship('Campus', lazy=True)
    address = relationship('Address', lazy=True)
    wishlist_items = relationship('CustomerWishlistItem', lazy=True)
    phone_numbers = relationship('PhoneNumber', lazy=True)
    loans = relationship('Loan', lazy=True)

    def __init__(self, ssn: str = None, email: str = None, pw_hash: str = None, first_name: str = None,
                 last_name: str = None, campus_id: int = None, type: str = 'STUDENT', cards: list[Card] = None,
                 can_borrow: bool = True, can_reserve: bool = True, books_borrowed: int = 0, books_reserved: int = 0,
                 is_active: bool = True, phone_numbers: list[PhoneNumber] = None, address: Address = None,
                 **other: dict):
        if len(other) > 0 or ssn is None or email is None or pw_hash is None \
                or phone_numbers is None or len(phone_numbers) == 0 or first_name is None or last_name is None \
                or campus_id is None or address is None or cards is None:
            raise InvalidRequestException

        self.ssn = ssn
        self.email = email
        self.password = pw_hash
        self.first_name = first_name
        self.last_name = last_name
        self.campus_id = campus_id
        self.type = type
        self.cards = cards
        self.phone_numbers = phone_numbers
        self.address = address
        self.can_borrow = can_borrow
        self.can_reserve = can_reserve
        self.books_borrowed = books_borrowed
        self.books_reserved = books_reserved
        self.is_active = is_active

    def __repr__(self):
        return f"Customer({self.first_name} {self.last_name} ({self.email}), borrowed: {self.books_borrowed}, reserved: {self.books_reserved})"

    @staticmethod
    def generate_password():
        return ''.join(choice(ascii_letters + digits) for i in range(randint(8, 12)))

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['CUSTOMER_SECRET_KEY'])
        try:
            ssn = s.loads(token)['ssn']
        except:
            return None
        return db.session.query(Customer).get(ssn)

    @staticmethod
    def translate_password(password):
        return bcrypt.generate_password_hash(password)

    def get_id(self) -> str:
        return self.ssn

    def update_record(self, first_name: str = None, last_name: str = None, email: str = None,
                      campus_id: int = None, address: dict = None, phone_numbers: bytearray = None, **other: dict):
        if len(other) > 0:
            raise InvalidRequestException

        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if email is not None:
            self.email = email
        if campus_id is not None:
            self.campus_id = campus_id
        if address is not None:
            self.address.update_record(**address)
        if type(phone_numbers) == list and len(phone_numbers) > 0:
            for number in self.phone_numbers:
                db.session.delete(number)
            for phone_number in phone_numbers:
                self.phone_numbers.append(PhoneNumber(customer_ssn=self.ssn, **phone_number))

        return self.get_relaxed_view()

    def get_reset_token(self, expires_sec=3600):
        s = Serializer(current_app.config['CUSTOMER_SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def get_relaxed_view(self) -> dict:
        cards = list(filter(lambda card: card.is_active, self.cards))
        return {
            'ssn': self.ssn,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'type': self.type,
            'card': cards[0].get_relaxed_view() if len(cards) > 0 else None,
            'campus': self.campus.get_relaxed_view(),
            'address': self.address.get_relaxed_view(),
            'phone_numbers': list(map(lambda phone: phone.get_relaxed_view(), self.phone_numbers)),
            'wishlist': list(map(lambda item: item.get_relaxed_view(), self.wishlist_items)),
            'can_borrow': self.can_borrow,
            'can_reserve': self.can_reserve,
            'is_active': self.is_active
        }

    def get_relaxed_v1_view(self) -> dict:
        return {
            'ssn': self.ssn,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'campus': self.campus.get_relaxed_view(),
            'address': self.address.get_relaxed_view(),
            'phone_numbers': list(map(lambda phone: phone.get_relaxed_view(), self.phone_numbers)),
        }

    def disable_record(self) -> None:
        self.is_active = False

    def enable_record(self) -> None:
        self.is_active = True


@login_manager.user_loader
def load_customer(ssn: str) -> any:
    login_type = session.get('login_type')
    if login_type == 'librarian':
        return db.session.query(Librarian).get(ssn)
    else:
        return db.session.query(Customer).get(ssn)


class CustomerWishlistItem(Base):
    __table__ = Table(
        'customer_wishlist_item',
        Base.metadata,
        Column('id', String, primary_key=True, server_default=FetchedValue()),
        Column('customer_ssn', String, ForeignKey('customer.ssn'), nullable=False),
        Column('book_isbn', String, ForeignKey('book.isbn'), nullable=False),
        Column('requested_at', DateTime),
        Column('picked_up', Boolean, default=False, nullable=False),
    )

    customer = relationship('Customer', lazy=True)
    book = relationship('Book', lazy=True)

    def __init__(self, id: str = None, customer_ssn: str = None, book_isbn: str = None,
                 requested_at: datetime = None, picked_up: bool = False, **other: dict):
        if len(other) > 0 or customer_ssn is None or book_isbn is None:
            raise InvalidRequestException

        self.id = id
        self.customer_ssn = customer_ssn
        self.book_isbn = book_isbn
        self.requested_at = requested_at
        self.picked_up = picked_up

    def __repr__(self):
        return f"Customer wishlist item(customer={self.customer_ssn}, book={self.book_isbn}, requested_at={self.requested_at}, picked_up={self.picked_up})"

    def request_now(self):
        self.requested_at = datetime.now()

    def get_relaxed_view(self) -> dict:
        return {
            'id': self.id,
            'book': {
                'isbn': self.book_isbn,
                'title': self.book.title,
            },
            'requested_at': self.requested_at,
            'picked_up': self.picked_up,
        }

    def get_librarian_relaxed_view(self) -> dict:
        return {
            'id': self.id,
            'book': {
                'isbn': self.book_isbn,
                'title': self.book.title,
            },
            'customer': {
                'ssn': self.customer_ssn,
                'full_name': f"{self.customer.first_name} {self.customer.last_name}"
            },
            'requested_at': self.requested_at,
            'picked_up': self.picked_up,
        }


class Librarian(Base, UserMixin):
    __table__ = Table(
        'librarian',
        Base.metadata,
        Column('ssn', String(20), primary_key=True),
        Column('email', String(100), nullable=False, unique=True),
        Column('password', String(60), nullable=False),
        Column('first_name', String(100), nullable=False),
        Column('last_name', String(100), nullable=False),
        Column('campus', Integer, ForeignKey('campus.address_id'), nullable=False),
        Column('position', String(30), nullable=False),
    )

    campus_address = relationship('Campus', lazy=True)

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

    @staticmethod
    def translate_password(password):
        return bcrypt.generate_password_hash(password)

    def __repr__(self):
        return f"Librarian({self.first_name} {self.last_name} ({self.email}), {self.position})"

    def get_id(self) -> str:
        return self.ssn

    def get_relaxed_view(self) -> dict:
        return {
            'ssn': self.ssn,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'campus': self.campus_address.get_relaxed_view(),
            'type': self.position,
        }


class LibrarianWishlistItem(Base):
    __table__ = Table(
        'library_wishlist_item',
        Base.metadata,
        Column('id', String, primary_key=True, server_default=FetchedValue()),
        Column('title', String(100), nullable=False),
        Column('description', Text),
    )

    def __init__(self, id: str = None, title: str = None, description: str = None, **other: dict):
        if len(other) > 0 or title is None or len(title) == 0 or description is None:
            raise InvalidRequestException

        self.id = id
        self.title = title
        self.description = description

    def __repr__(self):
        return f"Library wishlist item(title={self.title}, description={self.description})"

    def get_relaxed_view(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description if self.description is not None else '',
        }


class Loan(Base):
    __table__ = Table(
        'loan',
        Base.metadata,
        Column('id', String, primary_key=True, server_default=FetchedValue()),
        Column('book_isbn', String(30), ForeignKey('book.isbn', onupdate="cascade"), nullable=False),
        Column('customer_ssn', String(20), ForeignKey('customer.ssn'), nullable=False, index=True),
        Column('issued_by', String, ForeignKey('librarian.ssn'), nullable=False),
        Column('loaned_at', DateTime, default=datetime.utcnow, nullable=False, index=True),
        Column('returned_at', DateTime),
    )

    book = relationship('Book', lazy=True)
    customer = relationship('Customer', lazy=True)
    librarian = relationship('Librarian', lazy=True)

    def __init__(self, book_isbn: str = None, customer_ssn: str = None, issued_by: str = None,
                 loaned_at: datetime = None, returned_at: datetime = None, **other: dict):
        if len(other) > 0 or book_isbn is None or customer_ssn is None or issued_by is None:
            raise InvalidRequestException

        self.book_isbn = book_isbn
        self.customer_ssn = customer_ssn
        self.issued_by = issued_by
        self.loaned_at = loaned_at
        self.returned_at = returned_at

        if self.loaned_at is None:
            self.loaned_at = datetime.now()

    def __repr__(self):
        return f"Loan(book='{self.book_isbn}' customer='{self.customer_ssn}' issued_by='{self.issued_by}'" \
               f" ({self.loaned_at} - {self.returned_at})"

    def get_relaxed_view(self) -> dict:
        return {
            'id': self.id,
            'book': {
                'isbn': self.book_isbn,
                'title': self.book.title,
            },
            'issued_by': self.issued_by,
            'loaned_at': self.loaned_at,
            'returned_at': self.returned_at,
        }

    def close(self):
        self.returned_at = datetime.now()
