# -*- coding: UTF-8 -*-
import random
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from wallet.models import Commission,CommissionHistory

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
    Wyswietlanie lewej tabeli historii
    """
    bot_left_table='<table>'
    bot_left_table+='<thread><th>Data</th><th>Cena('+str(left_currency)+')</th><th>'+str(left_currency)+'</th><th>'+str(right_currency)+'</th>'
    for comm_history in CommissionHistory.objects.all():
        comm = Commission.objects.filter(id=comm_history.history.commission_id)[0]
        if comm_history.action == 1 and comm.destination_wallet.cryptocurrency.name == str(left_currency)  and comm.source_wallet.cryptocurrency.name == str(right_currency):
            bot_left_table+='<tr>'
            bot_left_table+='<td>'
            bot_left_table+=str(comm_history.executed_time)
            bot_left_table+='</td>'
            bot_left_table+='<td>'
            bot_left_table+=str(float(comm.source_amount)/float(comm.destination_amount))
            bot_left_table+='</td>'
            bot_left_table+='<td>' 
            bot_left_table+=str(comm.source_amount) 
            bot_left_table+='</td><td>'
            bot_left_table+=str(comm.destination_amount) 
            bot_left_table+='</td>'
            bot_left_table+='</tr>'
    bot_left_table+='</table>'
    dajax.assign('#bot_left_table', 'innerHTML',bot_left_table)
    
    """
    Wyswietlanie prawej tabeli historii
    """
    bot_right_table='<table>'
    bot_right_table+='<thread><th>Data</th><th>Cena('+str(left_currency)+')</th><th>'+str(left_currency)+'</th><th>'+str(right_currency)+'</th>'
    for comm_history in CommissionHistory.objects.all():
        comm = Commission.objects.filter(id=comm_history.history.commission_id)[0]
        if comm_history.action == 1 and comm.source_wallet.cryptocurrency.name == str(left_currency)  and comm.destination_wallet.cryptocurrency.name == str(right_currency):
            bot_right_table+='<tr>'
            bot_right_table+='<td>'
            bot_right_table+=str(comm_history.executed_time)
            bot_right_table+='</td>'
            bot_right_table+='<td>'
            bot_right_table+=str(float(comm.source_amount)/float(comm.destination_amount))
            bot_right_table+='</td>'
            bot_right_table+='<td>' 
            bot_right_table+=str(comm.source_amount) 
            bot_right_table+='</td><td>'
            bot_right_table+=str(comm.destination_amount) 
            bot_right_table+='</td>'
            bot_right_table+='</tr>'
    bot_right_table+='</table>'
    dajax.assign('#bot_right_table', 'innerHTML',bot_right_table)
    
    
    return dajax.json()