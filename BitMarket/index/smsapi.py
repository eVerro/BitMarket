# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User
import requests

class Smsapi:
    
    def __init__(self, username, password):
        """
        na razie jest tak, bo tak, a później bedzie bezpiczeniej... teraz ważne aby działało
        """
        self.u = username
        self.p = password
        self.url = 'https://ssl.smsapi.pl/sms.do'
        
    def sendConfirmationOfCommission(self, user):
        message = "Potwierdzenie stowrzenia zleceinia przez uzytkownika %s" % (user.username)
        params = {'to': user.phone_number, 'message': message}
        self.call(params)

    def sendConfirmationOfWithdraw(self, number,code, id):
        """
        Wysyła do użytkownika kod, który ma wprowadzić na stronie, aby potwierdzić wypłatę środków z konta.
        number - numer na który jest wysyłany kod
        code - kod potwierdzający
        id - numer zlecenia, kóre jest potwierdzane kodem.
        """
        message = "Aby potwierdzić zlecenie o numerze %s wpisz kod następujący kod 6 cyfrowy kod: %s" % (id ,code)
        params = {'to': number, 'message': message}
        self.call(params)

    def call(self, params=None):
        """
        Wysyła requesta z paramsami.
        """
        if params is None: params = {}
        params['username'] = self.u
        params['password'] = self.p
        params['from'] = self.domain_name
        
        # Zakomentuj poniższą linikę aby przyłączyć wysyłanie smsów z trybu testowego na rzeczywisty.
        params['test'] = 1
        
        response = requests.get(url=self.url,params=params)
        return response
    
    def test(self):
        params = {'to': "507606346", 'message': "Test"}
        params['username'] = self.u
        params['password'] = self.p
        params['from'] = ""
        params['test'] = 1
        response = requests.get(url=self.url,params=params)
        return response