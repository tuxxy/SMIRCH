from app import app, db
from flask import request, json
from api import Teli
from models import User, DID
import re


teli = Teli(app.config['TELI_TOKEN'], app.config['TELI_DID'])
TOPIC = ""

@app.route('/', methods=['POST'])
def main():
    # subscribe <nick>
    message = request.form.get('message').strip().split(' ')
    sender = User.query.filter_by(user_phone=request.form.get('source')).first()
    if sender is None:
        if message[0].lower() == 'subscribe' and len(message) >= 2:
            return subscribe_user(message, request.form.get('source'))
        else:
            teli.send_sms(int(request.form.get('source')),
                    "Subscribe to the Mojave SMS IRC by texting 'subscribe <nick>'")
        return json.dumps({'status': 'Call received'})
    else:
        if message[0].lower()[0] == '@':
            return priv_msg(message[0][1:].lower(), message[1:], sender)
        elif message[0].lower() == '/quit' or message[0].lower() == '/away':
            return unsub_user(sender)
        elif message[0].lower() == '/resub':
            return resub_user(sender, request.form.get('destination'))
        elif message[0].lower() == '/list':
            return list_users(sender)
        elif message[0].lower() == '/about':
            return send_about(sender)
        elif message[0].lower() == '/help':
            return send_help(sender)
        elif message[0].lower() == '/topic':
            if len(message) >= 2:
                return set_topic(sender, message)
            else:
                return view_topic(sender)
        elif message[0].lower() == '/nick':
            return set_nick(sender, message)
        else:
            return relay_sms(message, sender)
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
                    "Topic: {}\nText '/help' for commands.".format(TOPIC),
                    src=int(new_user.did.number))
            system_sms("{} has joined the chat!".format(new_user.nick))
    return json.dumps({'status': 'Call received'})


def unsub_user(user):
    user.is_subbed = False
    if not user.is_admin:
        user.did = None # Release the DID for others, unless you're an admin
    db.session.add(user)
    db.session.commit()
    teli.send_sms(int(user.user_phone), "Unsubbed from chat. Reply with '/resub' to rejoin!")
    system_sms("{} has quit the chat.".format(user.nick))
    return json.dumps({'status': 'Call received'})


def resub_user(user, pref_did):
    # Admins get to keep their DID
    if not user.is_admin:
        did = DID.query.filter_by(number=pref_did).first()
        # If someone isn't assigned the DID, use the preferred one.
        if did.user is None and pref_did != app.config['TELI_DID']:
            user.did = did
        else:
            did = DID.query.filter_by(user=None).first()
            if did is None:
                teli.send_sms(int(user.user_phone), "This chat is full, try again later.")
                return json.dumps({'status': 'Call received'})
            else:
                user.did = did
    user.is_subbed = True
    db.session.add(user)
    db.session.commit()
    teli.send_sms(int(user.user_phone), "Rejoined chat!")
    system_sms("{} has joined the chat!".format(user.nick))
    return json.dumps({'status': 'Call received'})


def priv_msg(nick, message, sender):
    user = User.query.filter_by(nick=nick).first()
    if user:
        if user.did:
            message = "PRIV~<{}> {}".format(sender.nick, ' '.join(message))
            teli.send_sms(int(user.user_phone), message, src=user.did.number)
    return json.dumps({'status': 'Call received'})


def list_users(sender):
    users = User.query.filter_by(is_subbed=True)
    subbed_users = []
    for user in users:
        subbed_users.append(user.nick)
    message = "\n".join(subbed_users)
    message += "\nTotal count: {}".format(len(subbed_users))
    teli.send_sms(int(sender.user_phone), message)
    return json.dumps({'status': 'Call received'})


def send_help(user):
    teli.send_sms(int(user.user_phone),
            "/help - Displays this menu\n@<nick> <message> - Private message user\n/quit OR /away - Unsubs from chat\n/resub - Resubscribes to chat\n/list - Lists users in chat\n/about - Displays info about the software")
    return json.dumps({'status': 'Call received'})


def set_topic(sender, message):
    global TOPIC
    if sender.is_admin:
        TOPIC = ' '.join(message[1:])
        system_sms('{} has changed the topic to: {}'.format(sender.nick, TOPIC))
    return json.dumps({'status': 'Call received'})


def view_topic(sender):
    teli.send_sms(int(sender.user_phone), TOPIC, src=int(sender.did.number))
    return json.dumps({'status': 'Call received'})


def set_nick(sender, message):
    new_nick = ""
    if len(message) >= 2:
        new_nick = re.sub('[^A-Za-z0-9_-]+', '', message[1]).lower()
    check_user = User.query.filter_by(nick=new_nick).first()
    if not check_user and len(new_nick) >= 3 and len(new_nick) <= 16:
        message = "{} has changed their nick to: {}".format(sender.nick, new_nick)
        sender.nick = new_nick
        db.session.add(sender)
        db.session.commit()
        system_sms(message)
    else:
        teli.send_sms(int(sender.user_phone), "Nick already in use.",
                src=int(sender.did.number))
    return json.dumps({'status': 'Call received'})


def send_about(user):
    teli.send_sms(int(user.user_phone),
            "SMIRCH is AGPLv3 software written in Python with Teli.net!.\nhttps://github.com/tuxxy/SMIRCH/\nAuthor: https://twitter.com/__tux")
    return json.dumps({'status': 'Call received'})


def relay_sms(message, sender): 
    if sender.is_subbed:
        if message[0].lower() == '/me' and len(message) >= 2:
            message = "* {} {}".format(sender.nick, ' '.join(message[1:]))
        else:
            message = "<{}> {}".format(sender.nick, ' '.join(message))
        for user in User.query.filter_by(is_subbed=True):
            # Don't send the sender the same message
            if sender != user:
                teli.send_sms(int(user.user_phone), message, src=int(user.did.number))
    else:
        teli.send_sms(int(sender.user_phone),
                "You are not subscribed. Text '/resub' to rejoin the chat.")
    return json.dumps({'status': 'Call received'})


def system_sms(message):
    for user in User.query.filter_by(is_subbed=True):
        teli.send_sms(int(user.user_phone), message, src=int(user.did.number))
    return json.dumps({'status': 'Call received'})
