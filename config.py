from os import urandom
from base64 import b64encode

class Config():
    SECRET_KEY = b64encode(urandom(66)).decode('utf-8')
    SESSION_KEY_BITS = 256
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:test123@localhost/smirch'
    TELI_TOKEN = ""
