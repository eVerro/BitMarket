# -*- coding: UTF-8 -*-
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from decimal import *
from django.utils.timezone import utc
from wallet.models import Commission, History, Cryptocurrency, UserProxy, \
    UserWallet
import datetime
import random


@dajaxice_register
def createCommision(request, source_amount, destination_amount, source_wallet_name, destination_wallet_name, end_date):
    dajax = Dajax()
    user = UserProxy.objects.get(id=request.user.id)
    try:
        user.newCommission(source_amount=Decimal(source_amount),
                               destination_amount=Decimal(destination_amount),
                               source_wallet=UserWallet.objects.filter(user=user, cryptocurrency=Cryptocurrency.objects.filter(name=source_wallet_name)[0])[0],
                               destination_wallet=UserWallet.objects.filter(user=user, cryptocurrency=Cryptocurrency.objects.filter(name=destination_wallet_name)[0])[0],
                               dead_line = datetime.datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S").replace(tzinfo=utc))
        dajax.script("show_msg();")
    except:
        dajax.script("show_err();")
    return dajax.json()
   
@dajaxice_register
def createOpenOrders(request):
    dajax = Dajax()
    open_orders_table='<table class="open_orders">'
    open_orders_table+='<thead><tr><th>Data wygaśnięcia</th><th>Akcja</th><th>Market</th><th>Cena(BTC)</th><th>Ilość</th><th>Razem(BTC)</th><th></th>'
    open_orders_table+='</tr></thead>'
    userproxy = UserProxy.objects.get(id=request.user.id)
    user_commisions = UserProxy.getCommissions( userproxy, sort="time_limit")
    
    for comm in user_commisions:
        open_orders_table+='<tr><td>'
        open_orders_table+=str(comm.time_limit.strftime("%Y-%m-%d %H:%M:%S"))
        open_orders_table+='</td><td>'
        if(comm.source_wallet.cryptocurrency.name == 'BTC'):
            open_orders_table+='Kupno'
        else:
            open_orders_table+='Sprzedaż'
        open_orders_table+='</td><td>'
        if(comm.source_wallet.cryptocurrency.name == 'LTC' or comm.destination_wallet.cryptocurrency.name == 'LTC'):
            open_orders_table+='BTC/LTC'
        else:
            open_orders_table+='BTC/GLD'
        open_orders_table+='</td><td>'
        if(comm.source_wallet.cryptocurrency.name == 'BTC'):
            open_orders_table+=str(format(Decimal(comm.source_price),'.10f'))
            open_orders_table+='</td><td>'
            open_orders_table+=str(format(Decimal(comm.destination_amount),'.10f'))
            open_orders_table+=' '+str(comm.destination_wallet.cryptocurrency.name)
            open_orders_table+='</td><td>'
            open_orders_table+=str(format(Decimal(comm.source_amount),'.10f'))
            open_orders_table+='</td>'
        else:
            open_orders_table+=str(format(Decimal(comm.destination_price),'.10f'))
            open_orders_table+='</td><td>'
            open_orders_table+=str(format(Decimal(comm.source_amount),'.10f'))
            open_orders_table+=' '+str(comm.source_wallet.cryptocurrency.name)
            open_orders_table+='</td><td>'
            open_orders_table+=str(format(Decimal(comm.destination_amount),'.10f'))
            open_orders_table+='</td>'
        open_orders_table+='<td>'
        open_orders_table+='<button class="sub_button" onclick="cancelCommission('+str(comm.id)+')">Anuluj</button>'
        open_orders_table+='</td></tr>'
    open_orders_table+='</table>'
    dajax.assign('#open_orders_table', 'innerHTML', open_orders_table)
    dajax.script('setScrollPosition();')
    return dajax.json()

@dajaxice_register
def createCommissionsHistory(request):
    dajax = Dajax()
    commisions_history_table = '<table class="history_commisions">'
    commisions_history_table+='<thead><tr><th>Data zrealizowania</th><th>Akcja</th><th>Market</th><th>Cena(BTC)</th><th>Ilość</th><th>Razem(BTC)</th>'
    commisions_history_table+='</tr></thead>'
    userproxy = UserProxy.objects.get(id=request.user.id)
    user_commissions_history = UserProxy.getExchangeHistory( userproxy, sort="executed_time")
    for comm in user_commissions_history:
        commisions_history_table+='<tr><td>'
        commisions_history_table+=str(comm.executed_time.strftime("%Y-%m-%d %H:%M:%S"))
        commisions_history_table+='</td><td>'
        if(comm.cryptocurrency_sold.name == 'BTC'):
            commisions_history_table+='Kupno'
        else:
            commisions_history_table+='Sprzedaż'
        commisions_history_table+='</td><td>'
        if(comm.cryptocurrency_sold.name == 'LTC' or comm.cryptocurrency_bought.name == 'LTC'):
            commisions_history_table+='BTC/LTC'
        else:
            commisions_history_table+='BTC/GLD'
        commisions_history_table+='</td><td>'
        if(comm.cryptocurrency_sold.name == 'BTC'):
            commisions_history_table+=str(format(Decimal(comm.sold_price),'.10f'))
            commisions_history_table+='</td><td>'
            commisions_history_table+=str(format(Decimal(comm.amount_bought),'.10f'))
            commisions_history_table+=' '+str(comm.cryptocurrency_bought.name)
            commisions_history_table+='</td><td>'
            commisions_history_table+=str(format(Decimal(comm.amount_sold),'.10f'))
            commisions_history_table+='</td>'
        else:
            commisions_history_table+=str(format(Decimal(comm.bought_price),'.10f'))
            commisions_history_table+='</td><td>'
            commisions_history_table+=str(format(Decimal(comm.amount_sold),'.10f'))
            commisions_history_table+=' '+str(comm.cryptocurrency_sold.name)
            commisions_history_table+='</td><td>'
            commisions_history_table+=str(format(Decimal(comm.amount_bought),'.10f'))
            commisions_history_table+='</td>'
        commisions_history_table+='</tr>'
    commisions_history_table+='</table>'
    dajax.assign('#commisions_history_table', 'innerHTML', commisions_history_table)
    return dajax.json()

@dajaxice_register
def realizeCommision(request, comm_id):
    dajax = Dajax()
    user = UserProxy.objects.get(id=request.user.id)
    commission = Commission.objects.get(id=comm_id)
    try:
        user.purchase(commission)
        dajax.script('show_realize_msg();');
    except:
        dajax.script('show_realize_err();');
    
    
    return dajax.json();

@dajaxice_register
def resetFields(request,site):
    dajax=Dajax()
    dajax.assign("#total_"+site, "innerHTML", "0.0000000000")
    dajax.assign("#provision_"+site, "innerHTML", "0.0000000000")
    dajax.assign("#after_provision_"+site, "innerHTML", "0.0000000000")
    return dajax.json()

@dajaxice_register
def validate(request,first_amount, second_amount, site):
    dajax=Dajax()
    getcontext().prec = 15
    total = Decimal(first_amount)*Decimal(second_amount)
    provision = Decimal(total)*Decimal(0.025)
    if site == "L":
        dajax.assign("#total_"+site, "innerHTML", str(total))
        dajax.assign("#provision_"+site, "innerHTML", str(provision))
        dajax.assign("#after_provision_"+site, "innerHTML", str(Decimal(total)+Decimal(provision)))
    if site == "R":
        dajax.assign("#total_"+site, "innerHTML", str(total))
        dajax.assign("#provision_"+site, "innerHTML", str(provision))
        dajax.assign("#after_provision_"+site, "innerHTML", str(Decimal(total)-Decimal(provision)))
        
    
    return dajax.json()

@dajaxice_register
def createTable(request, left_currency, right_currency):
    dajax = Dajax()
    """
    Wyswietlanie lewej tabeli zleceń
    """
    left_table='<table class="comm_table">'
    left_table+='<thead><tr><th>Cena('+str(left_currency)+')</th><th>'+str(right_currency)+'</th><th>Razem('+str(left_currency)+')</th>'
    left_table+='<th></th>'
    left_table+='</tr></thead>'
    
    for comm in Commission.getCommissions(cryptocurrency_sold=left_currency,cryptocurrency_bought=right_currency, sort='source_price').reverse():
        left_table+='<tr>'
        left_table+='<td>'
        left_table+=foramt_decimal(comm.source_price,8)
        left_table+='</td>'
        left_table+='<td>' 
        left_table+=foramt_decimal(comm.destination_amount,8)
        left_table+='</td><td>'
        left_table+=foramt_decimal(comm.source_amount,8)
        left_table+='</td>'
        if request.user.is_authenticated():
            left_table+='<td><button class="sub_button" onclick="Dajaxice.BitMarket.index.realizeCommision(Dajax.process,{''comm_id'':'+str(comm.id)+'});">Sprzedaj</button></td>'
        left_table+='</tr>'
    left_table+='</table>'
    dajax.assign('#left_table', 'innerHTML',left_table)
    
    """
    Wyswietlanie prawej tabeli zleceń
    """
    right_table='<table class="comm_table">'
    right_table+='<thead><tr><th>Cena('+str(left_currency)+')</th><th>'+str(right_currency)+'</th><th>Razem('+str(left_currency)+')</th>'
    right_table+='<th></th>'
    right_table+='</tr></thead>'
    for comm in Commission.getCommissions(cryptocurrency_sold=right_currency,cryptocurrency_bought=left_currency, sort='destination_price'):
        right_table+='<tr>'
        right_table+='<td>'
        right_table+=foramt_decimal(comm.destination_price,8)
        right_table+='</td>'
        right_table+='<td>'
        right_table+=foramt_decimal(comm.source_amount,8)
        right_table+='</td><td>'
        right_table+=foramt_decimal(comm.destination_amount,8)
        right_table+='</td>'
        if request.user.is_authenticated():
            right_table+='<td><button class="sub_button" onclick="Dajaxice.BitMarket.index.realizeCommision(Dajax.process,{''comm_id'':'+str(comm.id)+'});">Kup</button></td>'
        right_table+='</tr>'
    right_table+='</table>'
    dajax.assign('#right_table', 'innerHTML', right_table)
    
    
    
    """
    Wyswietlanie tabeli historii
    """
    history_table='<table class="history_table">'
    history_table+='<thead><tr><th>Data</th><th>Typ</th><th>Cena('+str(left_currency)+')</th><th>'+str(left_currency)+'</th><th>'+str(right_currency)+'</th>'
    history_table+='</tr></thead>'
    left_curr_object = Cryptocurrency.objects.filter(name = left_currency)[0]
    right_curr_object = Cryptocurrency.objects.filter(name = right_currency)[0]
    for comm_history in History.getExchangeHistory(left_curr_object, right_curr_object, 'executed_time').reverse():
        history_table+='<tr>'
        history_table+='<td>'
        history_table+=str(comm_history.executed_time.strftime("%Y-%m-%d %H:%M:%S"))
        history_table+='</td>'
        history_table+='<td>'
        if comm_history.cryptocurrency_sold.name == left_currency:
            history_table+='Sprzedaż'
        else:
            history_table+='Kupno'
        history_table+='</td>'
        history_table+='<td>'
        if comm_history.cryptocurrency_sold.name == left_currency:
            history_table+=foramt_decimal(comm_history.sold_price,8)
        else:
            history_table+=foramt_decimal(comm_history.bought_price,8)
        history_table+='</td>'
        history_table+='<td>' 
        history_table+=foramt_decimal(comm_history.amount_sold,8)
        history_table+='</td><td>'
        history_table+=foramt_decimal(comm_history.amount_bought,8) 
        history_table+='</td>'
        history_table+='</tr>'
    history_table+='</table>'
    dajax.assign('#history_table', 'innerHTML',history_table)  
    
    user_wallet = UserWallet.objects.get(user = request.user, cryptocurrency = Cryptocurrency.objects.get(name = left_currency));
    dajax.assign('#left_wallet','innerHTML',str(user_wallet.account_balance))
    user_wallet = UserWallet.objects.get(user = request.user, cryptocurrency = Cryptocurrency.objects.get(name = right_currency));
    dajax.assign('#right_wallet','innerHTML',str(user_wallet.account_balance))
    dajax.script('scrollRefresh();')
    return dajax.json()

def foramt_decimal(decimal, digits_count):
    if(decimal.adjusted()<0):
        d = digits_count
    else:
        d = digits_count - decimal.adjusted()
    return ("{:0<%ss}" % digits_count).format(("{:.%sf}" % d).format(decimal))

@dajaxice_register
def cancelComm(request, comm_id):
    dajax = Dajax()
    user = UserProxy.objects.get(id=request.user.id)
    coms  = Commission.objects.filter(id=comm_id)
    coms  = coms[0]
    user.cancelCommission(coms)
    dajax.script('RefreshTable();')
    return dajax.json()

