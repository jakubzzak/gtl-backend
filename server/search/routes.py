from flask import request, Blueprint, Response
from sqlalchemy.sql import text
from server.config import CustomResponse, InvalidRequestException
from server import db
from server.models import Book
from functools import reduce

search = Blueprint('search', __name__, url_prefix='/search')

groups = ['EVERYTHING', 'BOOK', 'ARTICLE', 'JOURNAL', 'MAP']
searchable_columns = ['TITLE', 'AUTHOR', 'AREA']


class SearchRequest:

    def __init__(self, offset: int = None, limit: int = None, phrase: str = None,
                 group: str = None, columns: bytearray = None, **other):
        if len(other) > 0:
            raise InvalidRequestException

        self.offset = offset
        self.limit = limit
        self.phrase = phrase
        self.groups = groups if group == 'EVERYTHING' else [group]
        self.columns = columns

    def is_valid(self):
        return self.offset is not None and self.offset >= 0 \
               and self.limit is not None and self.limit >= 5 \
               and self.phrase is not None and len(self.phrase) > 0 \
               and self.groups[0] is not None and self.groups[0] in groups \
               and self.columns is not None and len(self.columns) > 0 \
               and len(self.columns) > 0 \
               and (self.columns[0] in searchable_columns if len(self.columns) == 1 else reduce((lambda x, y: x and y), [col in searchable_columns for col in self.columns]))


@search.route("/", methods=['POST'])
@search.route("", methods=['POST'])
def search_in_catalog() -> Response:
    res = CustomResponse(data=[])
    try:
        req = SearchRequest(**request.json)
        if not req.is_valid():
            raise InvalidRequestException
        with db.engine.connect() as con:
            statement = text(f"""
            SELECT * FROM book 
            WHERE resource_type in {"('" + req.groups[0] + "')" if len(req.groups) == 1 else tuple(req.groups)} and
                (
                {"title like '%" + req.phrase + "%'" if 'TITLE' in req.columns else ''} 
                {" or " if 'AUTHOR' in req.columns and 'TITLE' in req.columns else '' } 
                {"author like '%" + req.phrase + "%'" if 'AUTHOR' in req.columns else ''} 
                {" or " if 'AREA' in req.columns and len(req.columns) > 1 else '' } 
                {"subject_area like '%" + req.phrase + "%'" if 'AREA' in req.columns else ''} 
                )
            ORDER BY isbn 
            OFFSET :offset ROWS 
            FETCH NEXT :limit ROW ONLY;
            """)
            rs = con.execute(statement, req.__dict__)
            data = []
            for row in rs:
                next = Book(**row)
                data.append(next.get_relaxed_view())
            res.set_data(data)
    except InvalidRequestException as e:
        res.set_error(e.message)
    return res.get_response()
