from django.shortcuts import render
from kiramama_app.models import *
import datetime

# Create your views here.

def default(request):
    return render(request, 'default.html')


#require session
def home(request):
    return render(request, 'home.html')


#require session
def communityhealthworker(request):
    return render(request, 'communityhealthworker.html')


#require session
def maternalhealth(request):
    return render(request, 'maternalhealth.html')


#require session
def childhealth(request):
    return render(request, 'childhealth.html')


#require session
def login(request):
    return render(request, 'login.html')


#require session
def logout(request):
    return render(request, 'logout.html')

