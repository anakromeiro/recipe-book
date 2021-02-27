from flask import request
from flask_restful import Resource
from http import HTTPStatus

from models.recipe import Recipe, recipe_list


class RecipeListResource(Resource):
    def get(self):
        data = []
        for recipe in recipe_list:
            if recipe.is_publish is True:
                data.append(recipe.data)
        return {'data': data}, HTTPStatus.OK

    def post(self):
        json_data = request.get_json()

        name = json_data.get('name')
        description = json_data.get('description')
        num_of_servings = json_data.get('num_of_servings')
        cooking_time = json_data.get('cooking_time')
        directions = json_data.get('directions')
        user_id = json_data.get('user_id')

        recipe = Recipe(name=name,
                        description=description,
                        num_of_servings=num_of_servings,
                        cooking_time=cooking_time,
                        directions=directions,
                        user_id=user_id)

        recipe.save()

        return recipe.data, HTTPStatus.CREATED


class RecipeResource(Resource):
    def get(self, recipe_id):
        recipe = next((recipe for recipe in recipe_list if recipe.id == recipe_id and recipe.is_publish == True), None)

        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        return recipe.data, HTTPStatus.OK

    def put(self, recipe_id):
        data = request.get_json()
        recipe = next((recipe for recipe in recipe_list if recipe.id == recipe_id), None)
        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        recipe.name = data['name']
        recipe.description = data['description']
        recipe.num_of_servings = data['num_of_servings']
        recipe.cooking_time = data['cook_time']
        recipe.directions = data['directions']
        return recipe.data, HTTPStatus.OK

    def delete(self, recipe_id):
        recipe = next((recipe for recipe in recipe_list if recipe.id == recipe_id and recipe.is_publish == True), None)
        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        recipe_list.remove(recipe)
        return {}, HTTPStatus.NO_CONTENT


class RecipePublishResource(Resource):
    def put(self, recipe_id):
        recipe = next((recipe for recipe in recipe_list if recipe.id == recipe_id), None)
        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        recipe.is_publish = True
        return {}, HTTPStatus.NO_CONTENT

    def delete(self, recipe_id):
        recipe = next((recipe for recipe in recipe_list if recipe.id == recipe_id), None)
        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        recipe.is_publish = False
        return {}, HTTPStatus.NO_CONTENT
