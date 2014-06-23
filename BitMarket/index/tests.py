from django.shortcuts import render_to_response
from wallet.models import WithdrawCodes
import datetime
def getCommissions(request):
    if(WithdrawCodes.confirm(user=request.user, code="52348", wallet_address="asdf", amount = "10")):
        print "fajnie"
    print "badum"
    return render_to_response('master/index.html', {'local': locals()})