# -*- coding: UTF-8 -*-
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from decimal import *
from django.utils.timezone import utc
from wallet.models import Commission, History, Cryptocurrency, UserProxy, \
    UserWallet
import datetime

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
        left_table+=str(format(Decimal(comm.source_price),'.10f'))
        left_table+='</td>'
        left_table+='<td>' 
        left_table+=str(format(Decimal(comm.destination_amount),'.10f'))
        left_table+='</td><td>'
        left_table+=str(format(Decimal(comm.source_amount),'.10f'))
        left_table+='</td>'
        if request.user.is_authenticated():
            left_table+='<td><button onclick="Dajaxice.BitMarket.index.realizeCommision(Dajax.process,{''comm_id'':'+str(comm.id)+'});">Sprzedaj</button></td>'
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
        right_table+=str(format(Decimal(comm.destination_price),'.10f'))
        right_table+='</td>'
        right_table+='<td>'
        right_table+=str(format(Decimal(comm.source_amount),'.10f'))
        right_table+='</td><td>'
        right_table+=str(format(Decimal(comm.destination_amount),'.10f'))
        right_table+='</td>'
        if request.user.is_authenticated():
            right_table+='<td><button onclick="Dajaxice.BitMarket.index.realizeCommision(Dajax.process,{''comm_id'':'+str(comm.id)+'});">Kup</button></td>'
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
    for comm_history in History.getExchangeHistory(left_curr_object, right_curr_object):
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
        history_table+=str(format(Decimal(comm_history.amount_bought)/Decimal(comm_history.amount_sold),'.10f'))
        history_table+='</td>'
        history_table+='<td>' 
        history_table+=str(comm_history.amount_sold) 
        history_table+='</td><td>'
        history_table+=str(comm_history.amount_bought) 
        history_table+='</td>'
        history_table+='</tr>'
    history_table+='</table>'
    dajax.assign('#history_table', 'innerHTML',history_table)  
    
    dajax.script('scrollRefresh();')
    return dajax.json()

@dajaxice_register
def cancelComm(request, comm_id):
    dajax = Dajax()
    user = UserProxy.objects.get(id=request.user.id)
    coms  = Commission.objects.filter(id=comm_id)
    coms  = coms[0]
    user.cancelCommission(coms)
    return dajax.json()
