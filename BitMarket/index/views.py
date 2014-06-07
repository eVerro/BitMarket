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
    History, Cryptocurrency
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


def gldc_view(request):
    local = locals()
    return render_to_response('currency/BTC_GLDC.html', {'local': local})


def ltc_view(request):
    local = locals()
    return render_to_response('currency/BTC_LTC.html', {'local': local})

def user(request):
    wallets = UserWallet.objects.filter(user=request.user)
    userhistories = History.objects.all()
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
    BTC_wallet = UserWallet.objects.filter(user=user, cryptocurrency=Cryptocurrency.objects.filter(name='BTC')[0])[0]
    GLDC_wallet = UserWallet.objects.filter(user=user, cryptocurrency=Cryptocurrency.objects.filter(name='GLDC')[0])[0]
    LTC_wallet = UserWallet.objects.filter(user=user, cryptocurrency=Cryptocurrency.objects.filter(name='LTC')[0])[0]
    now = datetime.datetime(2016, 3, 3, 1, 30) # datetime.datetime.utcnow().replace(tzinfo=utc)
    now = now.replace(tzinfo=utc)
    
    amounts = {}
    # z btc na gldc
    amounts['BTC_GLDC'] = [['0.09050625', 0.00000153], ["34.69569003","0.00058844"], ["191.96234052","0.00324800"], ["0.09901407","0.00000168"], ["0.09822053","0.00000166"], ["89.41710262","0.00208252"]]
    # z gldc na btc
    amounts['GLDC_BTC'] = [["125.00000000","0.00202000"], ["0.01500347","0.00000024"], ["0.04322170","0.00000068"], ["1111.00000000","0.01353198"], ["948.34890540","0.01148451"], ["15.00000000","0.00010500"], ["30.00000000","0.00003000"]]
    # z gldc na ltc
    amounts['GLDC_LTC'] = [["95.06421428","0.08871202"], ["1.05970468","1.05970468"], ["44.36339641","0.03966620"], ["1.28690191","0.00100000"], ["0.08190127","0.00004302"], ["10.00000000","0.00001660"], ["3232.98436240","3232.98436240"]]
    # z ltc na gldc
    amounts['LTC_GLDC'] = [["1.14547537","0.00110000"], ["8.99322994","0.00902201"], ["1.08854404","0.00113460"]]
    for amount in amounts['BTC_GLDC']:
        user.newCommission(source_amount=amount[0], destination_amount=amount[1], source_wallet=BTC_wallet, destination_wallet=GLDC_wallet, dead_line=now)
    for amount in amounts['GLDC_BTC']:
        user.newCommission(source_amount=amount[0], destination_amount=amount[1], source_wallet=GLDC_wallet, destination_wallet=BTC_wallet, dead_line=now)
    for amount in amounts['GLDC_LTC']:
        user.newCommission(source_amount=amount[0], destination_amount=amount[1], source_wallet=GLDC_wallet, destination_wallet=LTC_wallet, dead_line=now)
    for amount in amounts['LTC_GLDC']:
        user.newCommission(source_amount=amount[0], destination_amount=amount[1], source_wallet=LTC_wallet, destination_wallet=GLDC_wallet, dead_line=now)
    return render_to_response('master/index.html', {'local': locals()})
# def purchase(self, purchaser, purchased_commission):
def testPurchase(request):
    """
    link do testowania http://127.0.0.1:8000/pu
    """
    user = UserProxy.objects.get(id=request.user.id)
    coms  = Commission.objects.all()
    for com in coms:
        user.purchase(purchased_commission=com)
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
    amounts = {}
    amounts['Chrystian'] = ['345334.33445','232344.543432','234234.343434']
    amounts['Stefan'] = ['123123123.343434','1231233.4343','4324234.2324']
    amounts['Olga'] = ['123.45','1323.00','10.434']
    amounts['Karol'] = ['545.234','45545','123123']
    amounts['Piotr'] = ['10000','0','10']
    if user.username == 'Chrystian':
        user.deposit(wallet=wallets[0], wallet_address="1LxZ84RfAscG7KYpsnqit3i283g5WgBURQ", amount=amounts['Chrystian'][0])
        user.deposit(wallet=wallets[1], wallet_address="1LasdfcG7KYpsnqit3i283g5WasdfsddRQ", amount=amounts['Chrystian'][1])
        user.deposit(wallet=wallets[2], wallet_address="34jktnkjngkdfjgnkdbndkjfbnslWgBURQ", amount=amounts['Chrystian'][2])
    if user.username == 'Stefan':
        user.deposit(wallet=wallets[0], wallet_address="1LxZ84RfAscG7KYpsnqit3i283g5WgBDGF", amount=amounts['Stefan'][0])
        user.deposit(wallet=wallets[1], wallet_address="1LxZ84RfAscFRG7KYpsdf3i283g5WgBURQ", amount=amounts['Stefan'][1])
        user.deposit(wallet=wallets[2], wallet_address="1LxZ84RfAscG7KYpsnsdfg34tgrtgb45te", amount=amounts['Stefan'][2])
    if user.username == 'Olga':
        user.deposit(wallet=wallets[0], wallet_address="1LxZ84RfAscGVBW4NKJ5NG4L5T39RGRJKF", amount=amounts['Olga'][0])
        user.deposit(wallet=wallets[1], wallet_address="4RJ398FGJODVJNEROGVJWPE48G5UJPOTGI", amount=amounts['Olga'][1])
        user.deposit(wallet=wallets[2], wallet_address="RGN3QP2389GPJDFIVFSDVJASLFKDJSLKJF", amount=amounts['Olga'][2])
    if user.username == 'Karol':
        user.deposit(wallet=wallets[0], wallet_address="34H89F7OW34GHOIBUSNODB7IYODF8GB7SH", amount=amounts['Karol'][0])
        user.deposit(wallet=wallets[1], wallet_address="9DF8SB7SUY9ERJTOW489UGOCR8TVBJSDOP", amount=amounts['Karol'][1])
        user.deposit(wallet=wallets[2], wallet_address="VBWE4M8CUG59WU4CV9GW9ERCTGOSEIRGVL", amount=amounts['Karol'][2])
    if user.username == 'Piotr':
        user.deposit(wallet=wallets[0], wallet_address="UNG4OIF5YRG897FVYO9SD8BOI8SDUFBSD8", amount=amounts['Piotr'][0])
        user.deposit(wallet=wallets[1], wallet_address="POG4JKOPGYRU8TF9BUJOFIGBJOFGIBJBBG", amount=amounts['Piotr'][1])
        user.deposit(wallet=wallets[2], wallet_address="54GU8ED9RGUTVBJSDPOIUBJHSFGBU8F9G8", amount=amounts['Piotr'][2])
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