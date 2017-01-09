from django.shortcuts import render
from kiramama_app.models import *
import datetime

# Create your views here.

def default(request):
    return render(request, 'default.html')


#require session
def home(request):
    d = {}
    d['registeredmothers'] = Mother.objects.count()
    cpntotal = ReportCPN.objects.count()

    d['cpn1'] = 0.0
    d['cpn2'] = 0.0
    d['cpn3'] = 0.0
    d['cpn4'] = 0.0

    cpn1 = None
    cpn2 = None
    cpn3 = None
    cpn4 = None

    if (CPN.objects.filter(cpn_designation = "CPN1")):
        cpn1 = CPN.objects.get(cpn_designation = "CPN1")
    if (CPN.objects.filter(cpn_designation = "CPN2")):
        cpn2 = CPN.objects.get(cpn_designation = "CPN2")
    if (CPN.objects.filter(cpn_designation = "CPN3")):
        cpn3 = CPN.objects.get(cpn_designation = "CPN3")
    if (CPN.objects.filter(cpn_designation = "CPN4")):
        cpn4 = CPN.objects.get(cpn_designation = "CPN4")

    if (cpn1):
        d['cpn1'] = float(ReportCPN.objects.filter(concerned_cpn = cpn1).count())/ float(cpntotal) * 100.0

    if (cpn2):
        d['cpn2'] = float(ReportCPN.objects.filter(concerned_cpn = cpn2).count())/ float(cpntotal) * 100.0
        
    if (cpn3):
        d['cpn3'] = float(ReportCPN.objects.filter(concerned_cpn = cpn3).count())/ float(cpntotal) * 100.0

    if (cpn4):
        d['cpn4'] = float(ReportCPN.objects.filter(concerned_cpn = cpn4).count())/ float(cpntotal) * 100.0

    return render(request, 'home.html', d)


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

