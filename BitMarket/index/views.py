# -*- coding: UTF-8 -*-
# Create your views here.
from django.contrib.auth.models import auth
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.template import loader, RequestContext
from BitMarket.index.models import UserProfile
from wallet.models import UserWallet
from BitMarket.index.smsapi import Smsapi
import hashlib
from BitMarket.index.mailsender import MailSender


def index(request):
        local = locals()
        return render_to_response('master/index.html', {'local': local})


def aboutus(request):
        local = locals()
        return render_to_response('aboutus/aboutus.html', {'local': local})
    
    
def market(request):
        local = locals()
        return render_to_response('market/market.html', {'local': local})
    

def contact(request):
        local = locals()
        return render_to_response('contact/contact.html', {'local': local})
    
    
def register_view(request):
    return render_to_response('register/register.html')


def plnc_view(request):
    local = locals()
    return render_to_response('plnc/plnc.html', {'local': local})


def flt_view(request):
    local = locals()
    return render_to_response('flt/flt.html', {'local': local})

def user(request):
    local = locals()
    return render_to_response('user/user.html', {'local': local})

def user2(request):
    local = locals()
    UserWallet = UserWallet.objects.all()
    return render_to_response('user/user.html', {'local': local}, {'UserWallet': UserWallet})
def login(request):
            if request.method == 'POST':
                    username = request.POST['username']
                    password = request.POST['password']
                    user = auth.authenticate(username=username,
                                              password=password)
                    if user is not None and user.is_active:
                            auth.login(request, user)
                            return redirect("/")
                    else:
                            request.session['bad_login'] = 1
                            return render_to_response('aboutus/aboutus.html')


def register(request):
            if request.method == 'POST':
                    if request.POST['password'] == request.POST['password2']:
                            # Rejestracja
                            user = User.objects.create_user(username=request.POST['user'], email=request.POST['email'], password=request.POST['password'])
                            user.first_name = request.POST['name']
                            user.last_name = request.POST['name2']
                            #user.profile.miasto = request.POST['miasto']

                            user.save()
                            #p = UserProfile(id=user.id)
                            #p.miasto = request.POST['miasto']
                            #p.save()
                            # Logowanie
                            user = auth.authenticate(username=request.POST['user'], 
                                                     password=request.POST['password'])
                            auth.login(request, user)
                            #Redirect
                            return redirect("/")
            return render_to_response('register/index.html', {'local': locals()})


def logout_view(request):
    logout(request)
    return redirect("/")


def ajaxTest(request):
    return render_to_response('ajaxTest/ajax.html')

def sendMail(request):
        """
        Metoda wysyłająca maila w celu poinformowania o stworzeniu konta
        """
        sender = MailSender("xx")
        try:
            # Odkomentuj aby sprawdzić wysyłąnei testowwego maila
            response = sender.test()
            # Odkomentuj aby przy wysyłaniu brać dane zalogowanego użytkownika maila
            #user = request.user
            #response = sender.sendmail(user)
        except Exception:
            response = sender.createTemplateConfirmationOfRegistration()
            print "%s" % (response)
            # Odkomentuj aby sprawdzić wysyłąnei testowwego maila
            response = sender.test()
            # Odkomentuj aby przy wysyłaniu brać dane zalogowanego użytkownika maila
            #user = request.user
            #response = sender.sendmail(user)
        print "%s" % (response)
        return render_to_response('master/index.html', {'local': locals()})

def sendSms(request):
        """
        Metoda wysyłająca smsa w celu potwierdzenia stworzenia zlecenia
        """
        local = locals()
        hashs = hashlib.md5()
        hashs.update("xx")
        hashs = hashs.hexdigest()
        
        smsapi = Smsapi(username="chrystian.kislo@gmail.com", password=hashs)
        # Odkomentuj poniższą linikę, aby testować wysyłanie na konkretnych danych.
        response = smsapi.test()
        # Odkomentuj poniższe liniki, aby przy wysyłąniu wiadomości pobierać informacje od zalogowanego użytkownika
        #user = request.user
        #response = smsapi.sendConfirmationOfCommission(user)
        
        print "%s" % (hashs)
        print "%s" % (response.content)
        return render_to_response('master/index.html', {'local': local})
