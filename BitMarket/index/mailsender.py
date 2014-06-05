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
        print "%s %s hahahahhaha" % (user.username, user.code)
        try:
            template_content = [{'content': 'content', 'name': 'USERNAME'}]
            message = {
             'auto_html': True,
             'bcc_address': 'message.bcc_address@example.com',
             'from_email': 'mailtestsender4@gmail.com',
             'from_name': 'BitCoin',
             'global_merge_vars': [{'name': 'USERNAME', 'content': user.username},{'name': 'code', 'content': user.code}],
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