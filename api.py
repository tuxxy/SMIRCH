import requests

class Teli:
    TOKEN = ""
    API = ""

    def __init__(self, TOKEN):
        self.TOKEN = TOKEN
        self.API = "https://sms.teleapi.net/{}/send"

    def send_sms(self, src, dest, message):
        args = {
            'token': self.TOKEN,
            'source': src,
            'destination': dest,
            'message': message
        }
        return requests.post(self.API.format("sms"), data=args).status_code

    def send_mms(self, src, dest, file_name=None, file_data=None, file_url=None):
        args = {
            'token': self.TOKEN,
            'source': src,
            'destination': dest,
            'file_name': file_name,
            'file_data': file_data,
            'file_url': file_url
        }
        return requests.post(self.API.format("mms"), data=args).status_code
