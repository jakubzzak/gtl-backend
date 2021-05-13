from flask import request, Blueprint, Response, json
from server.config import CustomResponse
from functools import reduce


search = Blueprint('search', __name__)

groups = ['EVERYTHING', 'BOOK', 'ARTICLE', 'JOURNAL', 'MAP']

searchable_columns = ['TITLE', 'AUTHOR', 'AREA']


class SearchRequest:

    def __init__(self, phrase: str, group: str, columns: bytearray):
        self.phrase = phrase
        self.group = group
        self.columns = columns

    def is_valid(self):
        return self.phrase is not None and len(self.phrase) > 0 \
               and self.group in groups \
               and reduce((lambda x, y: x and y in searchable_columns), self.columns)


@search.route("/search", methods=['POST'])
def search_in_catalog():
    req = SearchRequest(**request.json)
    res = CustomResponse(data=[])
    if req.is_valid():
        res.set_data([])
        return res.get_response()
    res.set_error('Request is not valid')
    return res.get_response()
