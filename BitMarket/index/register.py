# -*- coding: UTF-8 -*-
from BitMarket.index.mailsender import MailSender
from BitMarket.index.models import UserNotConfirmed
from django.shortcuts import render_to_response, redirect
from test.test_compiler import s
import random



def register(request):
            if request.method == 'POST':
                    if request.POST['password'] == request.POST['password2']:
                            # Rejestracja
                            user = UserNotConfirmed.objects.create_user(username=request.POST['user'], email=request.POST['email'], password=request.POST['password'])
                            user.first_name = request.POST['name']
                            user.last_name = request.POST['name2']
                            user.phone_number = request.POST['phone']
                            
                            # Stworzenie codu do potwierdzenia dla używkonika
                            user.code = generateConfirmCode()
                            user.save()
                            
                            # Wysłanie maila z potwierdzeniem
                            sendConfirmMail(user)
                            
                            #Redirect
                            return redirect("/")
            return render_to_response('master/index.html', {'local': locals()})
        
def generateConfirmCode():
    """
    Metoda generująca kod, który jest wysyłany na maila użytkowniak w celu ustalenia zgodności, czy rejestrował się on na naszym portalu.
    """
    for x in range (0,30):
        r = random.randint(0,9)
        s += str(r)
    return s
    
def sendConfirmMail(user):
    """
    Metoda wysyłająca maila z kodem aktywującym konto
    """
    sender = MailSender("x")
    try:
        response = sender.sendConfirmationOfRegistration(user)
    except Exception:
        response = sender.createTemplateConfirmationOfRegistration()
        response = sender.sendConfirmationOfRegistration(user)
    print "%s" % (response)
    return 0

def checkConfirmLink(request, code):
    """
    Metoda potwierdzająca, czy otrzymany kod zgadza się, z którymś z kodów z niepotwerdzonych użytkowników. 
    """
    user = UserNotConfirmed.objects.filter(code=code)
    if user is not None:
        user[0].userconfim()
    else:
        raise Exception()
    return render_to_response('master/index.html', {'local': locals()})