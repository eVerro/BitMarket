from django.shortcuts import render_to_response
from wallet.models import Commission, History
import datetime
def getCommissions(request):
    for x in range(1,31):
        print History.getAverageExchangePriceOfDay(cryptocurrency_first="BTC", cryptocurrency_second="GLD", date=datetime.datetime(year=2014,month=6,day=x), source_price=0)
    return render_to_response('master/index.html', {'local': locals()})