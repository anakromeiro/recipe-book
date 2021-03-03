class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///recipebook.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'super-secret-key-2021'
    JWT_ERROR_MESSAGE_KEY = 'message'
