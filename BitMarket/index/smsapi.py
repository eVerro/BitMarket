from django.contrib.auth.models import User
import requests

class Smsapi:
    
    def __init__(self, username, password):
        """
        na razie jest tak, bo tak, a później bedzie bezpiczeniej... teraz ważne aby działało
        """
        self.u = username
        self.p = password
        self.domain_name
        self.url = '- https://ssl.smsapi.pl/sms.do'
        
    def sendConfirmationOfCommission(self, user):
        message = "Potwierdzenie stowrzenia zleceinia przez uzytkownika %s" % (user.username)
        params = {'to': user.phone_number, 'message': message}
        self.call(params)

    def call(self, params=None):
        """
        Wysyła requesta z paramsami.
        """
        if params is None: params = {}
        params['username'] = self.u
        params['password'] = self.p
        params['from'] = self.domain_name
        
        response = requests.get(url=self.url,params=params)
        return response