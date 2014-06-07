# -*- coding: UTF-8 -*-
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from decimal import *
from wallet.models import Commission, History, Cryptocurrency


@dajaxice_register
def realizeCommision(request, comm_id):
    return None;

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
    total = Decimal(first_amount)/Decimal(second_amount)
    provision = Decimal(total)*Decimal(0.025)
    
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
    for comm in Commission.objects.all():
        if comm.source_wallet.cryptocurrency.name == str(left_currency)  and comm.destination_wallet.cryptocurrency.name == str(right_currency):
            left_table+='<tr>'
            left_table+='<td>'
            getcontext().prec = 6
            left_table+=str(Decimal(comm.destination_amount)/Decimal(comm.source_amount))
            left_table+='</td>'
            left_table+='<td>' 
            left_table+=str(Decimal(comm.source_amount)) 
            left_table+='</td><td>'
            left_table+=str(Decimal(comm.destination_amount)) 
            left_table+='</td>'
            if request.user.is_authenticated():
                left_table+='<td><a href="#" onclick="Dajaxice.BitMarket.index.realizeCommision(Dajax.process,{''comm_id'':'+str(comm.id)+'});">Kup</a></td>'
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
    for comm in Commission.objects.all():
        if comm.destination_wallet.cryptocurrency.name == str(left_currency)  and comm.source_wallet.cryptocurrency.name == str(right_currency):
            
            right_table+='<tr>'
            right_table+='<td>'
            getcontext().prec = 6
            right_table+=str(Decimal(comm.destination_amount)/Decimal(comm.source_amount))
            right_table+='</td>'
            right_table+='<td>'
            right_table+=str(Decimal(comm.source_amount))
            right_table+='</td><td>'
            right_table+=str(Decimal(comm.destination_amount)) 
            right_table+='</td>'
            if request.user.is_authenticated():
                right_table+='<td><a href="#" onclick="Dajaxice.BitMarket.index.realizeCommision(Dajax.process,{''comm_id'':'+str(comm.id)+'});">Sprzedaj</a></td>'
            right_table+='</tr>'
            
    right_table+='</table>'
    dajax.assign('#right_table', 'innerHTML', right_table)
    
    
    
    """
    Wyswietlanie tabeli historii
    """
    history_table='<table class="comm_table">'
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
            history_table+='Kupno'
        else:
            history_table+='Sprzedaż'
        history_table+='</td>'
        history_table+='<td>'
        history_table+=str(float(comm_history.amount_sold)/float(comm_history.amount_bought))
        history_table+='</td>'
        history_table+='<td>' 
        history_table+=str(comm_history.amount_sold) 
        history_table+='</td><td>'
        history_table+=str(comm_history.amount_bought) 
        history_table+='</td>'
        history_table+='</tr>'
    history_table+='</table>'
    dajax.assign('#history_table', 'innerHTML',history_table)  
    return dajax.json()