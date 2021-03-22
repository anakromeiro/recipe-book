from flask import url_for
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
    avatar_url = ma.Method(serialize="dump_avatar_url")

    def load_password(self, value):
        return hash_password(value)

    def dump_avatar_url(self, user):
        if user.user_avatar:
            return url_for('static', filename='images/avatars/{}'.format(user.user_avatar), _external=True)
        else:
            return url_for('static', filename='images/assets/default_avatar.jpg', _external=True)
