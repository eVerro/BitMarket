from mandrill import Mandrill
import mandrill
from django.contrib.auth.models import User

class MailSender:
    
    def __init__(self, apikey):
        """
        apikey jest to klucz, który jest wykorzystywany do wysyłania maili.
        """
        m = Mandrill(apikey)
    
    def sendConfirmationOfRegistration(self, user):
        """
        Wysyła template do usera z prośbą o rejestracje.
        """
        try:
            user = User();
            template_content = [{'content': 'content', 'name': 'name'}]
            message = {
             'auto_html': True,
             'bcc_address': 'message.bcc_address@example.com',
             'from_email': 'mailtestsender4@gmail.com',
             'from_name': 'BitCoin',
             'global_merge_vars': [{'content': 'xx', 'name': 'xx'}],
             'important': True,
             'merge': True,
             'subject': 'Bitcoin: Confirm you registration',
             'tags': ['registration'],
             'to': [{'email': user.email,
                     'name': user.username,
                     'type': 'to'}]}
            result = self.m.messages.send_template(template_name='confirmation mail', template_content=template_content, message=message, async=False)
        except mandrill.Error, e:
            print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
            raise

    def createTemplateConfirmationOfRegistration(self, user):
        """
        Wysyła template do usera z prośbą o rejestracje.
        """
        context = r"Witaj /*|username|/*\
            Dziękujemy za zarejestrowanie się na naszej stronie BitMarket.\
            Życzymy Tobie udanych i szykich transakcj za pomocą naszego nowoczesnego systemu.\
            \
            Pozdrawiamy: Drużyna BitMarket"
        
        self.m.templates.add(self, name='confirmation mail', from_email=r"testmailsender4@gmail.com", 
                        from_name=r"Bit Market", subject="Confirmation", code="", text=context, publish=True, labels=["confirmation", "registration"]);
        
        