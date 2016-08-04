from app import app, db
from flask import request, json
from api import Teli
from models import User, DID
import re

teli = Teli(app.config['TELI_TOKEN'], app.config['TELI_DID'])


@app.route('/', methods=['POST'])
def main():
    # subscribe <nick>
    message = request.form.get('message').split(' ')
    if message[0].lower() == 'subscribe' and len(message) >= 2:
        return subscribe_user(message, request.form.get('source'))
    return json.dumps({'status': 'Call received'})

def subscribe_user(message, src):
    nick = re.sub('[^A-Za-z0-9_-]+', '', message[1])
    if len(nick) >= 2:
        # Grab the first available DID
        did = DID.query.filter_by(user_id=None).first()
        if did:
            new_user = User(nick, src, did)
            db.session.add(new_user)
            db.session.commit()
            teli.send_sms(
                    int(new_user.user_phone),
                    "Welcome to Mojave SMS IRC for DEFCON 24!\nWritten by @__tux for the Mojave!",
                    src=int(new_user.did.number))
    return json.dumps({'status': 'Call received'})
