# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User
import hashlib
import requests

class Smsapi:
    
    def __init__(self, username, password):
        """
        na razie jest tak, bo tak, a później bedzie bezpiczeniej... teraz ważne aby działało
        """
        hashs = hashlib.md5()
        hashs.update(password)
        password = hashs.hexdigest()
        
        self.u = username
        self.p = password
        self.url = 'https://ssl.smsapi.pl/sms.do'
        self.domain_name = ""

    def sendConfirmationOfWithdraw(self, number,code, id):
        """
        Wysyła do użytkownika kod, który ma wprowadzić na stronie, aby potwierdzić wypłatę środków z konta.
        number - numer na który jest wysyłany kod
        code - kod potwierdzający
        id - numer zlecenia, kóre jest potwierdzane kodem.
        """
        message = "Aby potwierdzic zlecenie o numerze %s wpisz nastepujacy 6 cyfrowy kod: %s" % (id ,code)
        params = {'to': "+48507606346", 'message': message}
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
        params['test'] = 0
        
        response = requests.get(url=self.url,params=params)
        return response