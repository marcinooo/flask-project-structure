"""Contains user resource endpoints handlers."""

from flask_restful import Resource
from flask_jwt_extended import jwt_required

from ..schemas.users import UserSchema
from ..models.users import User
from ..utils import success_response


class UserResource(Resource):
    """Manage single user."""

    @jwt_required()
    def get(self, user_id):
        """Returns user."""
        user = User.find_by_id(user_id)
        if user is None:
            return {'error': 'User not found.'}, 404
        user_schema = UserSchema.from_orm(user)
        return success_response(message='User data.', http_code=200, data=user_schema.dict())

    @jwt_required()
    def delete(self, user_id):
        """Deletes user."""
        user = User.find_by_id(user_id)
        if user is None:
            return {'error': 'User not found.'}, 404
        user.delete_from_db()
        return {'message': "User was deleted successfully."}, 200
