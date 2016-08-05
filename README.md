# SMIRCH
SMIRCH is an SMS/MMS based Relay Chat.

# About

SMIRCH uses prebought DIDs from https://Teli.net/ and assigns them to registered users.
Each user receives messages from their assigned DID.

When a user unsubscribes, the DID is released and given to the next available person.
If the user is an admin, the DID isn't released. This allows the admin to administer the channel, and receive messages even when unsubbed.

This software is in use for Mojave Payphone (760.733.9969) as a chat service for DEFCON 24 attendees.
Feel free to join the chat and have fun with everyone!

# TODO
* Allow MMS messages
* Make feature requests, pls

# LICENSE
SMIRCH is licensed under the AGPLv3. See the LICENSE file for details.
