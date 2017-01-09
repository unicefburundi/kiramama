from django.shortcuts import render
from kiramama_app.models import *
import datetime

# Create your views here.

def landing(request):
    return render(request, 'landing_page.html')
