from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(14), unique=True)
    user_phone = db.Column(db.String(20), unique=True)
    is_subbed = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    user_did = db.Relationship('DID', backref='user', lazy='dynamic')

    def __init__(self, nick, user_phone, user_did):
        self.nick = nick
        self.user_phone = user_phone


class DID(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
     
    def __init__(self, number):
        self.number = number
