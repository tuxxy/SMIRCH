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
    sender = User.query.filter_by(user_phone=request.form.get('source')).first()
    if sender is None:
        if message[0].lower() == '@subscribe' and len(message) >= 2:
            return subscribe_user(message, request.form.get('source'))
        else:
            teli.send_sms(int(request.form.get('source')),
                    "Subscribe to the Mojave SMS IRC by texting '@subscribe <nick>'")
        return json.dumps({'status': 'Call received'})
    else:
        elif message[0].lower() == '@unsub':
            return unsub_user(sender)
        elif message[0].lower() == '@resub':
            return resub_user(sender)
        elif message[0].lower()[0] == '@':
            return priv_msg(message[0][1:].lower(), message[1:], sender)
        elif message[0].lower() == '@help':
            return send_help(sender)
    return json.dumps({'status': 'Call received'})


def subscribe_user(message, src):
    nick = re.sub('[^A-Za-z0-9_-]+', '', message[1]).lower()
    if len(nick) >= 2:
        # Grab the first available DID
        did = DID.query.filter_by(user_id=None).first()
        if did:
            new_user = User(nick, src, did)
            db.session.add(new_user)
            db.session.commit()
            teli.send_sms(int(new_user.user_phone),
                    "Welcome to Mojave SMS IRC for DEFCON 24!\nWritten by @__tux for the Mojave!\nText '@help' for commands.",
                    src=int(new_user.did.number))
    return json.dumps({'status': 'Call received'})


def unsub_user(user):
    user.is_subbed = False
    if not user.is_admin:
        user.did = None # Release the DID for others, unless you're an admin
    db.session.add(user)
    db.session.commit()
    teli.send_sms(int(user.user_phone), "Unsubbed from chat. Reply with '@resub' to rejoin!")
    return json.dumps({'status': 'Call received'})


def resub_user(user):
    # Admins get to keep their DID
    if not user.is_admin:
        did = DID.query.filter_by(user=None).first()
        if did is None:
            teli.send_sms(int(user.user_phone), "This chat is full, try again later.")
            return json.dumps({'status': 'Call received'})
        else:
            user.did = did
    user.is_subbed = True
    teli.send_sms(int(user.user_phone), "Rejoined chat!")
    return json.dumps({'status': 'Call received'})


def priv_msg(nick, message, sender):
    user = User.query.filter_by(nick=nick).first()
    if user:
        if user.did:
            message = "PRIV~<{}> {}".format(sender.nick, ' '.join(message))
            teli.send_sms(int(user.user_phone), message, src=user.did.number)


def send_help(user):
    teli.send_sms(int(user.user_phone),
            "@help - Displays this menu\n@<nick> <message> - Private message user\n@unsub - Unsubs from chat\n@resub - Resubscribes to chat\n@about - Displays info about the software")
    return json.dumps({'status': 'Call received'})


def relay_sms(message, sender): 
    if sender.is_subbed:
        for user in User.query.filter_by(is_subbed=True):
            # Don't send the sender the same message
            if sender != user:
                message = ' '.join(message)
                teli.send_sms(int(user.user_phone), "<{}> {}".format(nick, message),
                        src=int(user.did.number))
    else:
        teli.send_sms(int(sender.user_phone),
                "You are not subscribed. Text 'subscribe' to rejoin the chat.",
                src=int(sender.did.number))
    return json.dumps({'status': 'Call received'})
