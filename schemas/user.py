from utils import hash_password
from extensions import ma


class UserSchema(ma.Schema):

    class Meta:
        ordered = True

    id = ma.Integer(dump_only=True)
    username = ma.String(required=True)
    email = ma.Email(required=True)
    password = ma.Method(required=True, deserialize="load_password")
    created_at = ma.DateTime(dump_only=True)
    updated_at = ma.DateTime(dump_only=True)

    def load_password(self, value):
        return hash_password(value)
