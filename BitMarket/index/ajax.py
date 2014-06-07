# -*- coding: UTF-8 -*-
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from wallet.models import Commission, CommissionHistory, History, Cryptocurrency
import random

@dajaxice_register
def randomize(request):
    dajax = Dajax()
    dajax.assign('#pln_gld', 'value', random.randint(1, 10))
    return dajax.json()

@dajaxice_register
def createTable(request, left_currency, right_currency):
    dajax = Dajax()
    
    """
    Wyswietlanie prawej tabeli zleceń
    """
    right_table='<table>'
    right_table+='<thread><th>Cena('+str(left_currency)+')</th><th>'+str(left_currency)+'</th><th>'+str(right_currency)+'</th>'
    if request.user.is_authenticated():
        right_table+='<th>#</th>'
    right_table+='</tr></thread>'
    for comm in Commission.objects.all():
        if comm.source_wallet.cryptocurrency.name == str(left_currency)  and comm.destination_wallet.cryptocurrency.name == str(right_currency):
            right_table+='<tr>'
            right_table+='<td>'
            right_table+=str(float(comm.source_amount)/float(comm.destination_amount))
            right_table+='</td>'
            right_table+='<td>'
            right_table+=str(comm.source_amount) 
            right_table+='</td><td>'
            right_table+=str(comm.destination_amount) 
            right_table+='</td>'
            if request.user.is_authenticated():
                right_table+='<td><a>Kup</a></td>'
            right_table+='</tr>'
    right_table+='</table>'
    dajax.assign('#right_table', 'innerHTML', right_table)
    
    
    """
    Wyswietlanie lewej tabeli zleceń
    """
    left_table='<table>'
    left_table+='<thread><th>Cena('+str(right_currency)+')</th><th>'+str(right_currency)+'</th><th>'+str(left_currency)+'</th>'
    if request.user.is_authenticated():
        left_table+='<th>#</th>'
    left_table+='</tr></thread>'
    for comm in Commission.objects.all():
        if comm.destination_wallet.cryptocurrency.name == str(left_currency)  and comm.source_wallet.cryptocurrency.name == str(right_currency):
            left_table+='<tr>'
            left_table+='<td>'
            left_table+=str(float(comm.source_amount)/float(comm.destination_amount))
            left_table+='</td>'
            left_table+='<td>' 
            left_table+=str(comm.source_amount) 
            left_table+='</td><td>'
            left_table+=str(comm.destination_amount) 
            left_table+='</td>'
            if request.user.is_authenticated():
                left_table+='<td><a>Kup</a></td>'
            left_table+='</tr>'
    left_table+='</table>'
    dajax.assign('#left_table', 'innerHTML',left_table)
    
    
    """
    Wyswietlanie tabeli historii
    """
    history_table='<table>'
    history_table+='<thread><th>Data</th><th>Typ</th><th>Cena('+str(left_currency)+')</th><th>'+str(left_currency)+'</th><th>'+str(right_currency)+'</th>'
    left_curr_object = Cryptocurrency.objects.filter(name = left_currency)[0]
    right_curr_object = Cryptocurrency.objects.filter(name = right_currency)[0]
    for comm_history in History.getExchangeHistory(left_curr_object, right_curr_object):
        comm = Commission.objects.filter(id=comm_history.history.commission_id)[0]
        history_table+='<tr>'
        history_table+='<td>'
        history_table+=str(comm_history.executed_time)
        history_table+='</td>'
        history_table+='<td>'
        if comm.source_wallet.name == left_currency:
            history_table+=left_currency+'>>'+right_currency
        else:
            history_table+=right_currency+'>>'+left_currency
        history_table+='</td>'
        history_table+='<td>'
        history_table+=str(float(comm.source_amount)/float(comm.destination_amount))
        history_table+='</td>'
        history_table+='<td>' 
        history_table+=str(comm.source_amount) 
        history_table+='</td><td>'
        history_table+=str(comm.destination_amount) 
        history_table+='</td>'
        history_table+='</tr>'
    history_table+='</table>'
    dajax.assign('#history_table', 'innerHTML',history_table)  
    return dajax.json()