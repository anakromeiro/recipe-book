from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, jwt_required

from models.recipe import Recipe


class RecipeListResource(Resource):

    def get(self):
        data = []

        for recipe in Recipe.get_all_published():
            data.append(recipe.data)

        return {'data': data}, HTTPStatus.OK

    @jwt_required(optional=False)
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()

        name = json_data.get('name')
        description = json_data.get('description')
        num_of_servings = json_data.get('num_of_servings')
        cooking_time = json_data.get('cooking_time')
        directions = json_data.get('directions')
        user_id = current_user

        recipe = Recipe(name=name,
                        description=description,
                        num_of_servings=num_of_servings,
                        cooking_time=cooking_time,
                        directions=directions,
                        user_id=user_id)

        recipe.save()

        return recipe.data, HTTPStatus.CREATED


class RecipeResource(Resource):

    @jwt_required(optional=True)
    def get(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if not recipe.is_published and recipe.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        return recipe.data, HTTPStatus.OK

    @jwt_required(optional=False)
    def put(self, recipe_id):

        data = request.get_json()
        recipe = Recipe.get_by_id(recipe_id)

        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.name = data['name']
        recipe.description = data['description']
        recipe.num_of_servings = data['num_of_servings']
        recipe.cooking_time = data['cooking_time']
        recipe.directions = data['directions']

        recipe.save()

        return recipe.data, HTTPStatus.OK

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
