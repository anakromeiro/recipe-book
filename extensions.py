from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_uploads import UploadSet, IMAGES
from mailgun import MailgunApi
from config import Config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
mailgun = MailgunApi(domain=Config.MAILGUN_DOMAIN, api_key=Config.MAILGUN_API_KEY)
image_set = UploadSet('images', IMAGES)
