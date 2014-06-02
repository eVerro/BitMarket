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
def createTable(request, source, destination):
    dajax = Dajax()
    pln_gld='<table>'
    pln_gld+='<th>PLN</th><th>GLD</th></tr><tr>'
    for comm in Commission.objects.all():
        if comm.source_wallet.cryptocurrency.name == str(source)  and comm.destination_wallet.cryptocurrency.name == str(destination):
            
            pln_gld+='<td>' 
            pln_gld+=str(comm.source_amount) 
            pln_gld+='</td><td>'
            pln_gld+=str(comm.destination_amount) 
            pln_gld+='</td>'
            if request.user.is_authenticated():
                pln_gld+='<td><input type="submit" value="Kup"/></td>'
            pln_gld+='</tr>'
    pln_gld+='</table>'
    
    dajax.assign('#plnclewa', 'innerHTML', pln_gld)
    gld_pln='<table>'
    gld_pln+='<th>GLD</th><th>PLN</th></tr><tr>'
    for comm in Commission.objects.all():
        if comm.destination_wallet.cryptocurrency.name == str(source)  and comm.source_wallet.cryptocurrency.name == str(destination):
            gld_pln+='<td>' 
            gld_pln+=str(comm.source_amount) 
            gld_pln+='</td><td>'
            gld_pln+=str(comm.destination_amount) 
            gld_pln+='</td>'
            if request.user.is_authenticated():
                gld_pln+='<td><input type="submit" value="Kup"/></td>'
            gld_pln+='</tr>'
    dajax.assign('#plncprawa', 'innerHTML',gld_pln)
    gld_pln+='</table>'
    
    return dajax.json()

@dajaxice_register
def updatecombo(request, option):
    dajax = Dajax()
    options = [['Madrid', 'Barcelona', 'Vitoria', 'Burgos'],
               ['Paris', 'Evreux', 'Le Havre', 'Reims'],
               ['London', 'Birmingham', 'Bristol', 'Cardiff']]
    out = []
    for option in options[int(option)]:
        out.append("<option value='#'>%s</option>" % option)
    dajax.assign('#gld_pln', 'innerHTML', 'dupa')
    dajax.assign('#pln_gld', 'innerHTML', 'dupa')
    
    dajax.assign('#combo2', 'innerHTML', ''.join(out))
    return dajax.json()
