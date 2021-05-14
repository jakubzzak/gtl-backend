from flask import request, Blueprint, Response
from sqlalchemy.sql import text
from server.config import CustomResponse, InvalidRequestException
from server import db \
    # , db_base
from server.models_old import Book
from functools import reduce

search = Blueprint('search', __name__, url_prefix='/search')

groups = ['EVERYTHING', 'BOOK', 'ARTICLE', 'JOURNAL', 'MAP']

searchable_columns = ['TITLE', 'AUTHOR', 'AREA']


class SearchRequest:

    def __init__(self, phrase: str = None, group: str = None, columns: bytearray = None, **other):
        self.phrase = phrase
        self.group = group
        self.columns = columns

    def is_valid(self):
        return self.phrase is not None and len(self.phrase) > 0 \
               and self.group is not None and self.group in groups \
               and self.columns is not None and len(self.columns) > 0 \
               and reduce((lambda x, y: x and y in searchable_columns), self.columns)


@search.route("/", methods=['POST'])
@search.route("", methods=['POST'])
def search_in_catalog() -> Response:
    res = CustomResponse(data=[])
    try:
        req = SearchRequest(**request.json)
        if not req.is_valid():
            raise InvalidRequestException
        with db.engine.connect() as con:
            # statement = text("""SELECT * FROM book WHERE resource_type<>:group""")
            statement = text("""SELECT top 3 * FROM book WHERE resource_type=:group""")
            rs = con.execute(statement, {'group': req.group})
            data = []
            for row in rs:
                next = Book(**row)
                data.append(next.get_relaxed_view())
            res.set_data(data)
    except InvalidRequestException as e:
        res.set_error(e.message)
    return res.get_response()
