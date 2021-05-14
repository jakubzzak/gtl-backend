from sqlalchemy import Table, Column, String, Text, Integer, Boolean
from sqlalchemy.orm import declarative_base

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

