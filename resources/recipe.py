import os
from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from extensions import image_set
from utils import save_image
from models.recipe import Recipe
from schemas.recipe import RecipeSchema

recipe_schema = RecipeSchema()
recipe_list_schema = RecipeSchema(many=True)
recipe_cover_schema = RecipeSchema(only=('recipe_cover_url', ))


class RecipeListResource(Resource):

    def get(self):
        recipes = Recipe.get_all_published()
        return recipe_list_schema.dump(recipes), HTTPStatus.OK

    @jwt_required(optional=False)
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()

        try:
            data = recipe_schema.load(data=json_data)
        except ValidationError as error:
            return {'message': 'Validation errors', 'errors': error}, HTTPStatus.BAD_REQUEST

        recipe = Recipe(**data)
        recipe.user_id = current_user

        recipe.save()

        return recipe_schema.dump(recipe), HTTPStatus.CREATED


class RecipeResource(Resource):

    @jwt_required(optional=True)
    def get(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if not recipe.is_published and recipe.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        return recipe_schema.dump(recipe), HTTPStatus.OK

    '''
    I'll let both PATCH and PUT as example, but only PATCH, in this case, would be enough
    '''

    @jwt_required(optional=False)
    def patch(self, recipe_id):

        json_data = request.get_json()
        try:
            data = recipe_schema.load(data=json_data, partial=('name',))
        except ValidationError as error:
            return error.messages, HTTPStatus.BAD_REQUEST

        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.name = data.get('name') or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.num_of_servings = data.get('num_of_servings') or recipe.num_of_servings
        recipe.cook_time = data.get('cooking_time') or recipe.cooking_time
        recipe.directions = data.get('directions') or recipe.directions

        recipe.save()
        return recipe_schema.dump(recipe), HTTPStatus.OK

    @jwt_required(optional=False)
    def put(self, recipe_id):

        json_data = request.get_json()
        try:
            data = recipe_schema.load(data=json_data, partial=('name',))
        except ValidationError as error:
            return error.messages, HTTPStatus.BAD_REQUEST

        recipe = Recipe.get_by_id(recipe_id)

        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.name = data.get('name')
        recipe.description = data.get('description')
        recipe.num_of_servings = data.get('num_of_servings')
        recipe.cook_time = data.get('cooking_time')
        recipe.directions = data.get('directions')

        recipe.save()
        return recipe_schema.dump(recipe), HTTPStatus.OK

    @jwt_required(optional=False)
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)

        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.remove()
        return {}, HTTPStatus.NO_CONTENT


class RecipePublishResource(Resource):

    @jwt_required(optional=False)
    def put(self, recipe_id):

        recipe = Recipe.get_by_id(recipe_id)

        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.is_published = True
        recipe.save()

        return {}, HTTPStatus.NO_CONTENT

    @jwt_required(optional=False)
    def delete(self, recipe_id):

        recipe = Recipe.get_by_id(recipe_id)

        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.is_published = False
        recipe.save()

        return {}, HTTPStatus.NO_CONTENT


class RecipeCoverImageUploadResource(Resource):

    @jwt_required(optional=False)
    def put(self, recipe_id):

        file = request.files.get('recipe_cover')
        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST
        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST

        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        if recipe.recipe_cover_image:
            cover_path = image_set.path(folder='recipe_covers', filename=recipe.recipe_cover_image)
            if os.path.exists(cover_path):
                os.remove(cover_path)

        filename = save_image(image=file, folder='recipe_covers')
        recipe.recipe_cover_image = filename
        recipe.save()

        return recipe_cover_schema.dump(recipe), HTTPStatus.OK

