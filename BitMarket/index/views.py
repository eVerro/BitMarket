# Create your views here.
from django.shortcuts import render_to_response


def index(request):
        return render_to_response('master/index.html')
    
def aboutus(request):
        return render_to_response('aboutus/aboutus.html')