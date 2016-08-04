import requests

class Teli:
    TOKEN = None
    SRC_DID = None
    API = None

    def __init__(self, TOKEN, SRC_DID):
        self.TOKEN = TOKEN
        self.SRC_DID = SRC_DID
        self.API = "https://sms.teleapi.net/{}/send"

    def send_sms(self, dest, message, src=None):
        if src is None:
            src = self.SRC_DID
        args = {
            'token': self.TOKEN,
            'source': src,
            'destination': dest,
            'message': message
        }
        return requests.post(self.API.format("sms"), data=args).status_code

    def send_mms(self, dest, file_name=None, file_data=None, file_url=None, src=None):
        if src is None:
            src = self.SRC_DID
        args = {
            'token': self.TOKEN,
            'source': src,
            'destination': dest,
            'file_name': file_name,
            'file_data': file_data,
            'file_url': file_url
        }
        return requests.post(self.API.format("mms"), data=args).status_code
