from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from webargs import fields
from webargs.flaskparser import use_kwargs
from models.user import User
from models.recipe import Recipe
from schemas.user import UserSchema
from schemas.recipe import RecipeSchema

user_schema = UserSchema()
# when the authenticated user accesses its users/<username> endpoint, they can get id, username, and email.
# But if they are not authenticated or are accessing other people's /users/<username> endpoint,
# the email address will be hidden.
user_public_schema = UserSchema(exclude=('email',))
recipe_list_schema = RecipeSchema(many=True)


class UserListResource(Resource):

    def post(self):

        json_data = request.get_json()

        data = user_schema.load(data=json_data)
        # if errors:
        #     return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        username = json_data.get('username')
        email = json_data.get('email')
        non_hash_password = json_data.get('password')

        if User.get_by_username(username):
            return {'message': 'username already used'}, HTTPStatus.BAD_REQUEST

        if User.get_by_email(email):
            return {'message': 'email already used'}, HTTPStatus.BAD_REQUEST

        if not non_hash_password:
            return {'message': 'password cannot be null'}, HTTPStatus.BAD_REQUEST

        user = User(**data)
        user.save()

        return user_schema.dump(user), HTTPStatus.CREATED


class UserResource(Resource):

    @jwt_required(optional=True)
    def get(self, username):

        user = User.get_by_username(username=username)

        if user is None:
            return {'message': 'user not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user == user.id:
            data = user_schema.dump(user)
        else:
            data = user_public_schema.dump(user)
        return data, HTTPStatus.OK


class MeResource(Resource):

    @jwt_required(optional=False)
    def get(self):
        user = User.get_by_id(user_id=get_jwt_identity())
        return user_schema.dump(user), HTTPStatus.OK


class UserRecipeListResource(Resource):

    @jwt_required(optional=True)
    @use_kwargs({"visibility": fields.Str(missing='public')})
    def get(self, username, visibility):

        user = User.get_by_username(username=username)
        if user is None:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()
        if current_user == user.id and visibility in ['all', 'private']:
            pass
        else:
            visibility = 'public'

        recipes = Recipe.get_all_by_user(user_id=user.id, visibility=visibility)

        return recipe_list_schema.dump(recipes), HTTPStatus.OK
