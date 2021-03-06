import os
from flask import request, url_for, render_template
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from http import HTTPStatus
from webargs import fields
from webargs.flaskparser import use_kwargs
from utils import generate_token, verify_token, save_image
from extensions import mailgun, image_set
from models.user import User
from models.recipe import Recipe
from schemas.user import UserSchema
from schemas.recipe import RecipeSchema

''' 
When the authenticated user accesses its users/<username> endpoint, they can get id, username, and email.
But if they are not authenticated or are accessing other people's /users/<username> endpoint,
the email address will be hidden.
'''
user_schema = UserSchema()
user_public_schema = UserSchema(exclude=('email',))
recipe_list_schema = RecipeSchema(many=True)
user_avatar_schema = UserSchema(only=('avatar_url', ))


class UserListResource(Resource):

    def post(self):

        json_data = request.get_json()

        # Checks if there is any validation error during serialization
        try:
            data = user_schema.load(data=json_data)
        except ValidationError as error:
            return {'message': 'Validation errors', 'errors': error}, HTTPStatus.BAD_REQUEST

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

        token = generate_token(user.email, salt='activate')
        subject = 'Please confirm your registration.'
        link = url_for('useractivateresource', token=token, external=True)
        html = render_template('activation_email.html', username=user.username, activation_link=link)
        mailgun.send_email(to=user.email, subject=subject, text='', html=html)

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


class UserActivateResource(Resource):

    def get(self, token):

        email = verify_token(token, salt='activate')

        if email is False:
            return {'message': 'Invalid token or token expired'}, HTTPStatus.BAD_REQUEST

        user = User.get_by_email(email=email)

        if not user:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND
        if user.is_active is True:
            return {'message': 'The user account is already activated'}, HTTPStatus.BAD_REQUEST

        user.is_active = True
        user.save()

        return {}, HTTPStatus.NO_CONTENT


class UserAvatarUploadResource(Resource):

    @jwt_required(optional=False)
    def put(self):

        file = request.files.get('avatar')
        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST
        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST

        user = User.get_by_id(user_id=get_jwt_identity())

        if user.user_avatar:
            avatar_path = image_set.path(folder='avatars', filename=user.user_avatar)
            if os.path.exists(avatar_path):
                os.remove(avatar_path)

        filename = save_image(image=file, folder='avatars')
        user.user_avatar = filename
        user.save()

        return user_avatar_schema.dump(user), HTTPStatus.OK
