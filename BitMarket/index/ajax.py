import random
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from wallet.models import Commission

@dajaxice_register
def flickr_save(request, new_title):
    dajax = Dajax()
    dajax.script('cancel_edit();')
    dajax.assign('#title', 'value', new_title)
    dajax.alert('Save complete using "%s"' % new_title)
    return dajax.json()

@dajaxice_register
def randomize(request):
    dajax = Dajax()
    dajax.assign('#result', 'value', random.randint(1, 10))
    return dajax.json()

@dajaxice_register
def createTable(request, source, destination):
    dajax = Dajax()
    pln_gld=''
    for comm in Commission.objects.all():
        if comm.source_wallet.cryptocurrency.name == str(source)  and comm.destination_wallet.cryptocurrency.name == str(destination):
            pln_gld+='<tr><td>' 
            pln_gld+=str(random.randint(1, 10)) 
            pln_gld+='</td><td>'
            pln_gld+=str(comm.destination_amount) 
            pln_gld+='</td>'
            if request.user.is_authenticated():
                pln_gld+='<td><input type="submit" value="Kup"/></td>'
            pln_gld+='</tr>'
            
    dajax.assign('#pln_gld', 'innerHTML', pln_gld)

    gld_pln=''
    for comm in Commission.objects.all():
        if comm.destination_wallet.cryptocurrency.name == str(source)  and comm.source_wallet.cryptocurrency.name == str(destination):
            gld_pln+='<tr><td>' 
            gld_pln+=str(comm.source_amount) 
            gld_pln+='</td><td>'
            gld_pln+=str(comm.destination_amount) 
            gld_pln+='</td>'
            if request.user.is_authenticated():
                gld_pln+='<td><input type="submit" value="Kup"/></td>'
            gld_pln+='</tr>'
    dajax.assign('#gld_pln', 'innerHTML', gld_pln)
    
    return dajax.json()