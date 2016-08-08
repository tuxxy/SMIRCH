# SMIRCH
SMIRCH is an SMS/MMS based Relay Chat.

# About

SMIRCH uses prebought DIDs from https://Teli.net/ and assigns them to registered users.
Each user receives messages from their assigned DID.

When a user unsubscribes, the DID is released and given to the next available person.
If the user is an admin, the DID isn't released. This allows the admin to administer the channel, and receive messages even when unsubbed.

This software is in use for Mojave Payphone (760.733.9969) as a chat service for DEFCON 24 attendees.
Feel free to join the chat and have fun with everyone!

# Configuration
1. Setup a virtualenv and install the dependencies in requirements.txt.
2. Install MySQL server implementation of your choice (I use mariaDB) and create a database called 'smirch'.
3. Edit config.py and replace the `root` and `test123` on line 7 (`SQLALCHEMY_DATABASE_URI`) with your db's user and password. Then on lines 8 & 9, replace `TELI_TOKEN` with your Teli API token and replace the `TELI_DID` with the DID that you want server messages to be sent from. (In the Mojave's case, it is the 760 number.) This must be a number you own on Teli.
4. Source your virtualenv and execute `python -c "from app import views;views.db.create_all()`.
5. Get any number of DIDs that you want from the Teli API. (The Mojave uses 200.) Download the CSV file, and add them to the database by using SQLAlchemy. I did this by parsing the CSV file and adding them via `db.session.add()`, the doing `db.session.commit()`. `db.session.add()` requires a SQLAlchemy model object, so you can create a DID by importing `DID` from models.py and do `DID('123456789')`. Of course, replace the DID with the DID you parsed from the CSV file. I'll probably add a script to do this later.
5. Run the app using your preferred method. I use gunicorn for the Mojave.
6. Configure your webserver however you like and configure Teli to post to your application whenever it receives an SMS/MMS.
7. Done!

# TODO
* Make feature requests, pls
* See the Issue tracker

# LICENSE
SMIRCH is licensed under the AGPLv3. See the LICENSE file for details.
