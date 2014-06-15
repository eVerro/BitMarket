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
    
def deposit(request,wallet):
        local = locals()
        return render_to_response('user/deposit.html', {'local': local,'wallet': wallet})
     
def withdraw(request,wallet):
        local = locals()
        return render_to_response('user/withdraw.html', {'local': local,'wallet': wallet})
    
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
    local = locals()
    return render_to_response('user/user.html', {'local': local})

def cancel(request, cancel):
    user = UserProxy.objects.get(id=request.user.id)
    coms  = Commission.objects.filter(id=cancel)
    coms  = coms[0]
    user.cancelCommission(coms)
    return render_to_response('user/cancel.html', {'local': locals()})

def open_orders(request):
    userproxy=UserProxy.objects.get(id=request.user.id)
    userhistories = UserProxy.getCommissionHistory( userproxy, sort=None)
    local = locals()
    return render_to_response('user/open_orders.html', {'local': local})

def trade_history(request):
    userproxy=UserProxy.objects.get(id=request.user.id)
    userhistories = UserProxy.getCommissionHistory( userproxy, sort=None)
    local = locals()
    return render_to_response('user/trade_history.html', {'local': local})

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
    # LTC_wallet = UserWallet.objects.filter(user=user, cryptocurrency=Cryptocurrency.objects.filter(name='LTC')[0])[0]
    now = datetime.datetime(2016, 3, 3, 1, 30) # datetime.datetime.utcnow().replace(tzinfo=utc)
    now = now.replace(tzinfo=utc)
    
    amounts = {}
    # z btc na gldc
    amounts['BTC_GLDC'] = [['118.15364928','0.00289595'], ['13000.00000000','0.31850000'], ['62.50000000','0.00150125'], ['0.07320617','0.00000176'], ['95.57052837','0.00229369'], ['0.00831675','0.00000020'], ['600.20000000','0.01436879'], ['0.01533690','0.00000037'], ['67.07883316','0.00159782'], ['500.00000000','0.01190000'], ['0.01968030','0.00000047'], ['0.00989845','0.00000023'], ['0.03026240','0.00000071'], ['2218.63352576','0.05235975'], ['0.01136775','0.00000027'], ['0.00713206','0.00000017'], ['88.55125019','0.00208007'], ['0.00858950','0.00000020'], ['5000.00000000','0.11700000'], ['0.01295047','0.00000030'], ['0.00577676','0.00000013'], ['0.00724267','0.00000017'], ['2397.72782131','0.05574717'], ['0.00581036','0.00000013'], ['0.00582539','0.00000014'], ['0.01170124','0.00000027'], ['4.33087917','0.00010000'], ['0.00587091','0.00000014'], ['448.67488564','0.01034196'], ['0.00588621','0.00000014'], ['2840.00000000','0.06532000'], ['0.00590159','0.00000014'], ['33.20720852','0.00076277'], ['5.72000000','0.00013122'], ['0.02679008','0.00000061'], ['7.00331651','0.00015961'], ['0.00598735','0.00000014'], ['5000.00000000','0.11375000'], ['0.00750727','0.00000017'], ['0.01055427','0.00000024'], ['2000.00000000','0.04520000'], ['0.01821756','0.00000041'], ['2206.06690179','0.04965857'], ['10226.08746573','0.23008697'], ['5000.00000000','0.11245000'], ['0.01682612','0.00000038'], ['1500.00000000','0.03360000'], ['333.33333333','0.00745667'], ['220.00000000','0.00491700'], ['1350.00000000','0.03010500'], ['500.00000000','0.01112500'], ['714.27829294','0.01585698'], ['1274.78849029','0.02824931'], ['1050.86261534','0.02327661'], ['134.87649983','0.00298212'], ['1000.00000000','0.02210000'], ['5555.00000000','0.12237665'], ['15000.00000000','0.33000000'], ['3.41000000','0.00007454'], ['1253.75894463','0.02739463'], ['220.00000000','0.00480480'], ['500.00000000','0.01090000'], ['134.75488496','0.00292418'], ['250.00000000','0.00542250'], ['1000.00000000','0.02167000'], ['13.01077535','0.00027882'], ['62.50000000','0.00131813'], ['283.20400000','0.00596994'], ['3.51187688','0.00007385'], ['8611.00000000','0.18091711'], ['2.95481432','0.00006187'], ['1466.11084222','0.03067104'], ['2.41632051','0.00005009'], ['1.93244316','0.00003927'], ['1111.00000000','0.02228666'], ['324.44299479','0.00650508'], ['1505.85599643','0.03014724'], ['25100.00000000','0.50200000'], ['10000.00000000','0.19990000'], ['7500.00000000','0.14707500'], ['5.11247444','0.00010000'], ['4.76455916','0.00009281'], ['22155.61177482','0.42095662'], ['1000.00000000','0.01830000'], ['0.55667423','0.00001016'], ['100.00000000','0.00180000'], ['1022.15872874','0.01823531'], ['30533.59005413','0.54258190'], ['80.00000000','0.00140000'], ['1000.00000000','0.01702000'], ['1470.00000000','0.02500470'], ['15100.00000000','0.25670000'], ['7056.75334053','0.11820062'], ['38.00000000','0.00062814'], ['1000.00000000','0.01641000'], ['0.90103440','0.00001458'], ['14.16050698','0.00022841'], ['10194.51309227','0.16311221'], ['2200.00000000','0.03517800'], ['250.81154529','0.00394025']]
    # z gldc na btc
    amounts['GLDC_BTC'] = [['178.92148687','0.00422970'],['8.74228624','0.00020763'],['100.61837588','0.00239270'],['0.09416166','0.00000235'],['0.03843672','0.00000096'],['100.00000000','0.00249400'],['0.00527553','0.00000013'],['363.21434714','0.00907673'],['4830.23082589','0.12075577'],['0.01573827','0.00000039'],['391.62424362','0.00982977'],['0.02724806','0.00000069'],['0.35730042','0.00000905'],['0.03957153','0.00000101'],['0.27205707','0.00000697'],['0.03886162','0.00000101'],['0.18965517','0.00000492'],['0.02963212','0.00000078'],['55.40882598','0.00145005'],['0.02075825','0.00000055'],['88.08790177','0.00232200'],['0.03252898','0.00000087'],['127.00000000','0.00337947'],['334.05991535','0.00889267'],['1000.00000000','0.02663000'],['0.00598206','0.00000016'],['400.00000000','0.01066400'],['0.00596527','0.00000016'],['180.00000000','0.00480960'],['0.00950700','0.00000025'],['139.84242379','0.00374638'],['0.02238657','0.00000060'],['1000.00000000','0.02699000'],['2221.04852145','0.05996831'],['0.01635238','0.00000044'],['4.71698113','0.00012792'],['0.01853081','0.00000051'],['500.00000000','0.01365500'],['0.03426638','0.00000094'],['75.00000000','0.00206850'],['0.01019072','0.00000028'],['90.00000000','0.00249030'],['0.00451531','0.00000013'],['1368.11154298','0.03792405'],['29.18017484','0.00080946'],['0.02128623','0.00000059'],['103.16736352','0.00287837'],['0.00445965','0.00000012'],['1003.66837858','0.02804249'],['0.00445008','0.00000012'],['100.00000000','0.00280000'],['50.00000000','0.00141000'],['500.00000000','0.01415500'],['80.00000000','0.00226560'],['10.00000000','0.00028500'],['1597.00000000','0.04575405'],['2000.00000000','0.05792000'],['110.00000000','0.00319000'],['4.78468900','0.00014000'],['500.00000000','0.01465500'],['57.73721071','0.00169459'],['63.91213527','0.00190969'],['6000.00000000','0.17946000'],['90.00000000','0.00269550'],['44.00000000','0.00131912'],['1535.86539631','0.04607596'],['4151.03025611','0.12469695'],['30.00000000','0.00090150'],['1250.00000000','0.03801250'],['28.07814625','0.00085638'],['22.83347915','0.00070396'],['30.00000000','0.00092640'],['3.31235508','0.00010248'],['712.82460284','0.02209756'],['150.00000000','0.00468600'],['250.00000000','0.00785250'],['4.04694456','0.00012800'],['987.00000000','0.03136686'],['200.00000000','0.00638000'],['1535.23633400','0.04912756'],['100.00000000','0.00322100'],['250.00000000','0.00810250'],['24.56101647','0.00079725'],['187.50000000','0.00611250'],['200.00000000','0.00653000'],['100.00000000','0.00328800'],['2407.44371340','0.07944564'],['300.00000000','0.00993600'],['500.00000000','0.01657500'],['0.90580000','0.00003019'],['250.00000000','0.00835250'],['3099.35014376','0.10491300'],['2075.64825989','0.07032296'],['44273.26016134','1.50086352'],['2382.71803646','0.08101241'],['1000.00000000','0.03402000'],['500.00000000','0.01706000'],['3.00120048','0.00010249'],['20.96830893','0.00071858'],['250.00000000','0.00860250']]
    # z gldc na ltc
    # amounts['BTC_LTC'] = [["95.06421428","0.08871202"], ["1.05970468","1.05970468"], ["44.36339641","0.03966620"], ["1.28690191","0.00100000"], ["0.08190127","0.00004302"], ["10.00000000","0.00001660"], ["3232.98436240","3232.98436240"]]
    # z ltc na gldc
    # amounts['LTC_BTC'] = [["1.14547537","0.00110000"], ["8.99322994","0.00902201"], ["1.08854404","0.00113460"]]
    i=0
    for amount in amounts['BTC_GLDC']:
        print (user.id-1+i)%UserProxy.objects.all().count()
        if (user.id-1+i)%UserProxy.objects.all().count()==0:
            print (user.id-1+i)%UserProxy.objects.all().count()
            print "qwertyuiop"
            user.newCommission(source_amount=amount[1], destination_amount=amount[0], source_wallet=BTC_wallet, destination_wallet=GLDC_wallet, dead_line=now)
        i=i+1
    i=0
    for amount in amounts['GLDC_BTC']:
        if (user.id-1+i)%UserProxy.objects.all().count()==0:
            user.newCommission(source_amount=amount[0], destination_amount=amount[1], source_wallet=GLDC_wallet, destination_wallet=BTC_wallet, dead_line=now)
        i=i+1
    # for amount in amounts['BTC_LTC']:
    #     user.newCommission(source_amount=amount[0], destination_amount=amount[1], source_wallet=BTC_wallet, destination_wallet=LTC_wallet, dead_line=now)
    # for amount in amounts['LTC_BTC']:
    #     user.newCommission(source_amount=amount[0], destination_amount=amount[1], source_wallet=LTC_wallet, destination_wallet=BTC_wallet, dead_line=now)
    return render_to_response('master/index.html', {'local': locals()})
# def purchase(self, purchaser, purchased_commission):
def testPurchase(request):
    """
    link do testowania http://127.0.0.1:8000/pu
    """
    user = UserProxy.objects.get(id=request.user.id)
    #print user
    coms  = Commission.objects.all()
    for com in coms:
        try:
            user.purchase(purchased_commission=com)
        except Exception:
            print "pijmy bawmy się, siallalalala"
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
    amounts = {}
    amounts['Chrystian'] = ['345334.33445','232344.543432','234234.343434']
    amounts['Stefan'] = ['123123123.343434','1231233.4343','4324234.2324']
    amounts['Olga'] = ['123.45','1323.00','10.434']
    amounts['Karol'] = ['545.234','45545','123123']
    amounts['Piotr'] = ['10000','10000','10']
    users = UserProxy.objects.all()
    for user in users:
        wallets = UserWallet.objects.filter(user=user)
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
    for history in History.getBoughtHistory(Cryptocurrency.objects.filter(name='BTC')[0],Cryptocurrency.objects.filter(name='GLDC')[0], sort='amount_sold'):
        print history
    return render_to_response('master/index.html', {'local': locals()})
def getExchangeHistory(request):
    for history in History.getExchangeHistory(Cryptocurrency.objects.filter(name='GLDC')[0],Cryptocurrency.objects.filter(name='BTC')[0], sort='amount_sold'):
        print history
        print '1'
    return render_to_response('master/index.html', {'local': locals()})