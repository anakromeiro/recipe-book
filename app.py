from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_uploads import configure_uploads, patch_request_class
from config import Config
from extensions import db, jwt, ma, image_set
from resources.user import UserListResource, UserResource, MeResource, UserRecipeListResource, UserActivateResource, \
    UserAvatarUploadResource
from resources.recipe import RecipeListResource, RecipeResource, RecipePublishResource, RecipeCoverImageUploadResource
from resources.token import TokenResource, RefreshResource, RevokeResource, black_list


def create_app():
    recipe_book_app = Flask(__name__)
    recipe_book_app.config.from_object(Config)

    register_extensions(recipe_book_app)
    register_resources(recipe_book_app)
    configure_uploads(recipe_book_app, image_set)
    patch_request_class(recipe_book_app, 10 * 1024 * 1024)

    return recipe_book_app


def register_extensions(recipe_book_app):
    db.app = recipe_book_app
    db.init_app(recipe_book_app)
    ma.app = recipe_book_app
    ma.init_app(recipe_book_app)
    jwt.app = recipe_book_app
    jwt.init_app(recipe_book_app)
    migrate = Migrate(recipe_book_app, db)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(self, decrypted_token):
        jti = decrypted_token['jti']
        return jti in black_list


def register_resources(recipe_book_app):
    api = Api(recipe_book_app)

    api.add_resource(UserListResource, '/users')
    api.add_resource(UserResource, '/users/<string:username>')
    api.add_resource(UserRecipeListResource, '/users/<string:username>/recipes')
    api.add_resource(UserActivateResource, '/users/activate/<string:token>')
    api.add_resource(UserAvatarUploadResource, '/users/avatar')
    api.add_resource(TokenResource, '/token')
    api.add_resource(RefreshResource, '/refresh')
    api.add_resource(RevokeResource, '/revoke')
    api.add_resource(MeResource, '/me')
    api.add_resource(RecipeListResource, '/recipes')
    api.add_resource(RecipeResource, '/recipe/<int:recipe_id>')
    api.add_resource(RecipePublishResource, '/recipe/<int:recipe_id>/publish')
    api.add_resource(RecipeCoverImageUploadResource, '/recipe/<int:recipe_id>/cover')


if __name__ == '__main__':
    app = create_app()
    app.run()
