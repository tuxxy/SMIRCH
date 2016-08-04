from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(14), unique=True)
    user_phone = db.Column(db.String(20), unique=True)
    user_did = db.Column(db.String(), unique=True)
    is_subbed = db.Column(db.Boolean, default=False)

    def __init__(self, nick, user_phone, user_did):
        self.nick = nick
        self.user_phone = user_phone
        self.user_did = user_did
