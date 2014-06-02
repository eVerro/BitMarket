# -*- coding: UTF-8 -*-
from mandrill import Mandrill
import mandrill
from django.contrib.auth.models import User

class MailSender:
    
    def __init__(self, apikey):
        """
        apikey jest to klucz, który jest wykorzystywany do wysyłania maili.
        """
        self.m = Mandrill(apikey)
    
    def sendConfirmationOfRegistration(self, user):
        """
        Wysyła template do usera z prośbą o rejestracje.
        """
        try:
            user = User();
            template_content = [{'content': 'content', 'name': 'name'}]
            message = {
             'auto_html': False,
             'bcc_address': 'message.bcc_address@example.com',
             'from_email': 'mailtestsender4@gmail.com',
             'from_name': 'BitCoin',
             'global_merge_vars': [{'username': user.username, 'code': user.code}],
             'important': True,
             'merge': True,
             'subject': 'Potwierdzenie rejestracji na stronie BitMarket',
             'tags': ['registration'],
             'to': [{'email': user.email,
                     'name': user.username,
                     'type': 'to'}]}
            result = self.m.messages.send_template(template_name='confirmation mail', template_content=template_content, message=message, async=False)
        except mandrill.Error, e:
            print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
            raise
        return result

    def createTemplateConfirmationOfRegistration(self):
        """
        Wysyła template do usera z prośbą o rejestracje.
        """
        context = r"Witaj /*|username|/*\
            Ten mail został wysłany w celu weryfikacji Twojego konta mailowego. \
            Proszę potwierdź swój mail klikając na link pod spodem, bądź wklejając go do paska url. \
            http://127.0.0.1:8000/registrationconfirm//*code/*\
            Pozdrawiamy: Drużyna BitMarket"
        
        result = self.m.templates.add(name='confirmation mail', from_email=r"testmailsender4@gmail.com",from_name=r"Bit Market", 
                             subject="Confirmation", code="test test test", text=context, publish=True, labels=["confirmation", "registration"]);
        return result
        
    def test(self):
        """
        Wysyła testowego template na mail testmailsender4@gmail.com.
        """
        try:
            user = User();
            template_content = [{'content': 'Tutaj powinno wstawić TO', 'name': 'username'}]
            message = {
             'auto_html': False,
             'bcc_address': 'testmailsender4@gmail.com',
             'from_email': 'testmailsender4@gmail.com',
             'from_name': 'BitCoin',
             'global_merge_vars': [{'content': 'xx', 'name': 'xx'}],
             'important': True,
             'merge': True,
             'subject': 'Test: Wysyłam se testa',
             'tags': ['test1','test2','test3'],
             'to': [{'email': 'testmailsender4@gmail.com',
                     'name': 'Testnamebocoinnegonibydać',
                     'type': 'to'}]}
            result = self.m.messages.send_template(template_name='confirmation mail', template_content=template_content, message=message, async=False)
        except mandrill.Error, e:
            print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
            raise
        return result
        