"""Contains example of api resource."""

from flask_restful import Resource
from flask_jwt_extended import jwt_required

from ..auth.utils import require_active_account
from ..utils import success_response


class ToDoResource(Resource):
    """Fake resource to demonstrate app."""
    @jwt_required()
    @require_active_account
    def get(self, todo_id):
        """Returns to-do resource."""
        fake_to_do = {
            'id': todo_id,
            'content': 'Deploy app!'
        }
        return success_response(message='ToDo data.', http_code=200, data=fake_to_do)
