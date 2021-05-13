from flask import request, Blueprint

main = Blueprint('main', __name__)


@main.route('/test', methods=['GET', 'POST'])
def test():
    return {'text': 'Hello, World!'}


@main.route('/test/<uuid:id>', methods=['GET', 'POST'])
def test_uuid(id: id) -> dict:
    return {
        'text': 'Hello, World!',
        'id': id,
    }
