# Create your views here.
from django.contrib.auth.models import auth
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.shortcuts import render_to_response, redirect
from BitMarket.index.models import UserProfile



def index(request):
        local = locals();
        return render_to_response('master/index.html', {'local' : local})
    
def aboutus(request):
        local = locals();
        return render_to_response('aboutus/aboutus.html', {'local' : local})
    
def register_view(request):
    return render_to_response('register/register.html')
    
def login(request):
            if request.method == 'POST':
                    username = request.POST['username']
                    password = request.POST['password']
                    user = auth.authenticate(username=username, password=password)
                    if user is not None and user.is_active:
                            auth.login(request, user)
                            return redirect("/")
                    else:
                            request.session['bad_login'] = 1
                            return render_to_response('aboutus/aboutus.html')
                        
def rejestracja(request):
            if request.method == 'POST':
                    if request.POST['password'] == request.POST['password2']:
                            # Rejestracja
                            user = User.objects.create_user(username=request.POST['user'], email=request.POST['email'],password=request.POST['password'])
                            user.first_name=request.POST['name']
                            user.last_name=request.POST['name2']
                            #user.profile.miasto = request.POST['miasto']

                            user.save()
                            #p = UserProfile(id=user.id)
                            #p.miasto = request.POST['miasto']
                            #p.save()
                           
                            # Logowanie
                            user = auth.authenticate(username=request.POST['user'],password=request.POST['password'])
                            auth.login(request, user)
                           
                            #Redirect
                            return redirect("/")
     
            return render_to_response('register/index.html', {'local' : locals()})
        
def logout_view(request):
    logout(request)
    return redirect("/")