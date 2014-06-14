from django.shortcuts import render_to_response
from wallet.models import Commission
def getCommissions(request):
    for commission in Commission.getCommissions(cryptocurrency_sold='BTC',cryptocurrency_bought='GLDC', sort='source_amount'):
        print commission
    return render_to_response('master/index.html', {'local': locals()})