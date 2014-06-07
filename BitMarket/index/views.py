# -*- coding: UTF-8 -*-
# Create your views here.
from BitMarket.index.mailsender import MailSender
from BitMarket.index.models import Newss, UserProfile
from BitMarket.index.smsapi import Smsapi
from django.contrib.auth import logout
from django.contrib.auth.models import User, auth
from django.shortcuts import render_to_response, redirect
from django.utils.timezone import utc
from wallet.models import UserProxy, UserWallet, Commission, WithdrawCodes, \
    History, CommissionHistory, Cryptocurrency
import datetime
import hashlib



def index(request):
        latest_news_list = Newss.objects.all().order_by('-pub_date')
        local = locals()
        return render_to_response('master/index.html', {'local': local,'latest_news_list': latest_news_list})
        #return render_to_response('master/index.html', {'local': local})

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
    wallets = UserWallet.objects.filter(user=request.user)
    histories = CommissionHistory.objects.all()
    i=0
    userhistory=[None]*len(histories)
    while(i<len(histories)):
        if(histories[i].history.seller==request.user):
            userhistory[i]=histories[i]
        i=i+1
    i=0
    account=0
    while i<len(wallets):
        account=account+wallets[i].account_balance
        i=i+1
    local = locals()
    return render_to_response('user/user.html', {'local': local})

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
    local = locals()
    return render_to_response('ajaxTest/ajax.html', {'local': locals()})

# def newCommission(self, source_amount, destination_amount, wallet_source, wallet_destination, dead_line):
def testNewCommission(request):
    """
    link do testowania http://127.0.0.1:8000/nc
    """
    user = UserProxy.objects.get(id=request.user.id)
    wallets = UserWallet.objects.filter(user=user)
    now = datetime.datetime(2016, 3, 3, 1, 30) # datetime.datetime.utcnow().replace(tzinfo=utc)
    now = now.replace(tzinfo=utc)
    # now += 1
    print wallets.count()
    user.newCommission(source_amount=10, destination_amount=20, source_wallet=wallets[1], destination_wallet=wallets[2], dead_line=now)
    return render_to_response('master/index.html', {'local': locals()})
# def purchase(self, purchaser, purchased_commission):
def testPurchase(request):
    """
    link do testowania http://127.0.0.1:8000/pu
    """
    user = UserProxy.objects.get(id=request.user.id)
    coms  = Commission.objects.all()
    coms  = coms[0]
    user.purchase(purchased_commission=coms)
    return render_to_response('master/index.html', {'local': locals()})
# def withdraw(self, wallet, wallet_address, amount):
def testWithdrawRequest(request):
    """
    link do testowania http://127.0.0.1:8000/wr
    """
    user = UserProxy.objects.get(id=request.user.id)
    wallets = UserWallet.objects.filter(user=user)
    user.withdraw(wallet=wallets[0], wallet_address="test_address", amount=10)
    return render_to_response('master/index.html', {'local': locals()})
# def confim(self, user, code):
def testWithdraw(request, code):
    """
    link do testowania http://127.0.0.1:8000/wi
    """
    user = UserProxy.objects.get(id=request.user.id)
    wallets = UserWallet.objects.filter(user=user)
    
    hashs = hashlib.md5()
    hashs.update(code)
    code = hashs.hexdigest()
        
    confirm = WithdrawCodes.objects.filter(code=code)
    confirm[0].confirm(user=user, code=code)
    return render_to_response('master/index.html', {'local': locals()})
# def deposit(self, wallet, wallet_address, amount):
def testDeposit(request):
    """
    link do testowania http://127.0.0.1:8000/de
    """
    user = UserProxy.objects.get(id=request.user.id)
    wallets = UserWallet.objects.filter(user=user)
    user.deposit(wallet=wallets[0], wallet_address="test_address", amount=10)
    return render_to_response('master/index.html', {'local': locals()})
def testCancelCommission(request):
    """
    link do testowania http://127.0.0.1:8000/cc
    """
    user = UserProxy.objects.get(id=request.user.id)
    coms  = Commission.objects.all()
    coms  = coms[0]
    user.cancelCommission(coms)
    return render_to_response('master/index.html', {'local': locals()})

def checkOverdue(self):
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    overdue_commissions = Commission.objects.extra(where=['time_limit>%s'], params=[now])
    for commission in overdue_commissions:
        commission.overdue()
    commission.delete()
    
def getBoughtHistory(request):
    for history in History.getBoughtHistory(Cryptocurrency.objects.filter(name='PLN')[0],Cryptocurrency.objects.filter(name='GLD')[0]):
        print history
    return render_to_response('master/index.html', {'local': locals()})
def getExchangeHistory(request):
    for history in History.getExchangeHistory(Cryptocurrency.objects.filter(name='PLN')[0],Cryptocurrency.objects.filter(name='GLD')[0]):
        print history
        print '1'
    return render_to_response('master/index.html', {'local': locals()})