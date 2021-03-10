from extensions import ma
from schemas.user import UserSchema
from marshmallow import validate, validates, post_dump


class RecipeSchema (ma.Schema):

    def validate_num_of_servings(n):
        if n < 1:
            raise ma.ValidationError('Number of servings must be greater than 0.')
        if n > 50:
            raise ma.ValidationError('Number of servings must not be greater than 50.')

    class Meta:
        ordered = True

    id = ma.Integer(dump_only=True)
    name = ma.String(required=True, validate=[validate.Length(max=100)])
    description = ma.String(validate=[validate.Length(max=200)])
    num_of_servings = ma.Integer(validate=validate_num_of_servings)
    is_published = ma.Boolean(dump_only=True)
    author = ma.Nested(UserSchema, attribute='user', dump_only=True, only=['id', 'username'])
    created_at = ma.DateTime(dump_only=True)
    updated_at = ma.DateTime(dump_only=True)
    '''
     dump_only = True is causing an error in the following fields:
     marshmallow.exceptions.ValidationError: {'cooking_time': ['Unknown field.']}
     https://stackoverflow.com/questions/54391524/sqlalchemy-property-causes-unknown-field-error-in-marshmallow-with-dump-only/54405610
    '''
    cooking_time = ma.Integer()
    directions = ma.String(validate=[validate.Length(max=1000)])

    @validates('cooking_time')
    def validate_cooking_time(self, value):
        if value < 1:
            raise ma.ValidationError('Cook time must be greater than 0.')
        if value > 300:
            raise ma.ValidationError('Cook time must not be greater than 300.')

    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        if many:
            return {'data': data}
        return data

