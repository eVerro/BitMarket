# -*- coding: UTF-8 -*-
import random
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from wallet.models import Commission

@dajaxice_register
def randomize(request):
    dajax = Dajax()
    dajax.assign('#pln_gld', 'value', random.randint(1, 10))
    return dajax.json()

@dajaxice_register
def createTable(request, left_currency, right_currency):
    dajax = Dajax()
    right_table='<table>'
    right_table+='<thread><th>Cena('+str(left_currency)+')</th><th>'+str(left_currency)+'</th><th>'+str(right_currency)+'</th>'
    if request.user.is_authenticated():
        right_table+='<th>#</th>'
    right_table+='</tr></thread>'
    for comm in Commission.objects.all():
        if comm.source_wallet.cryptocurrency.name == str(left_currency)  and comm.destination_wallet.cryptocurrency.name == str(right_currency):
            right_table+='<tr">'
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
    left_table='<table>'
    left_table+='<thread><th>Cena('+str(right_currency)+')</th><th>'+str(right_currency)+'</th><th>'+str(left_currency)+'</th>'
    if request.user.is_authenticated():
        left_table+='<th>#</th>'
    left_table+='</tr></thread>'
    for comm in Commission.objects.all():
        if comm.destination_wallet.cryptocurrency.name == str(left_currency)  and comm.source_wallet.cryptocurrency.name == str(right_currency):
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
    dajax.assign('#left_table', 'innerHTML',left_table)
    left_table+='</table>'
    
    
    
    return dajax.json()