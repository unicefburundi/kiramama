from django.shortcuts import render
from kiramama_app.models import *
from health_administration_structure_app.models import *
from django.http import HttpResponse
import datetime
import json
#from django.http import JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict

# Create your views here.

def default(request):
    d = {}
    return render(request, 'default.html', d)


#require session
def home(request):
    d = {}
    d["pagetitle"] = "Home"
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

    d['number_of_chw'] = 0.0
    d['percentage_of_active_chw'] = 0.0
    d['percentage_of_not_active_chw'] = 0.0

    d['total_delivery'] = 0.0
    d['percentage_delivery_at_home'] = 0.0
    d['percentage_delivery_on_road'] = 0.0
    d['percentage_delivery_at_HF'] = 0.0
    d['percentage_delivery_at_hospital'] = 0.0
    d['percentage_delivery_at_CDS'] = 0.0

    d['vac_list'] = []


    if (CPN.objects.filter(cpn_designation = "CPN1")):
        cpn1 = CPN.objects.get(cpn_designation = "CPN1")
    if(CPN.objects.filter(cpn_designation = "CPN2")):
        cpn2 = CPN.objects.get(cpn_designation = "CPN2")
    if(CPN.objects.filter(cpn_designation = "CPN3")):
        cpn3 = CPN.objects.get(cpn_designation = "CPN3") 
    if(CPN.objects.filter(cpn_designation = "CPN4")):
        cpn4 = CPN.objects.get(cpn_designation = "CPN4")

    if (cpn1):
        d['cpn1'] = float(ReportCPN.objects.filter(concerned_cpn = cpn1).count())/ float(cpntotal) * 100.0

    if (cpn2):
        d['cpn2'] = float(ReportCPN.objects.filter(concerned_cpn = cpn2).count())/ float(cpntotal) * 100.0
        
    if (cpn3):
        d['cpn3'] = float(ReportCPN.objects.filter(concerned_cpn = cpn3).count())/ float(cpntotal) * 100.0

    if (cpn4):
        d['cpn4'] = float(ReportCPN.objects.filter(concerned_cpn = cpn4).count())/ float(cpntotal) * 100.0


    #What is the percentage of active and inactive CHWs
    if(CHW.objects.all()):
        d['number_of_chw'] = CHW.objects.count()

        if(CHW.objects.filter(is_active = True)):
            d['percentage_of_active_chw'] = CHW.objects.filter(is_active = True).count() / float(d['number_of_chw']) * 100
            

        if(CHW.objects.filter(is_active = False)):
            d['percentage_of_not_active_chw'] = CHW.objects.filter(is_active = False).count() / float(d['number_of_chw']) * 100


    #Statistics about delivery
    if(ReportNSC.objects.all()):
        d['total_delivery'] = ReportNSC.objects.count()
        if(ReportNSC.objects.filter(birth_location__location_category_designation__iexact = 'HP')):
            d['percentage_delivery_at_hospital'] = ReportNSC.objects.filter(birth_location__location_category_designation__iexact = 'HP').count() / float(d['total_delivery']) * 100
        if(ReportNSC.objects.filter(birth_location__location_category_designation__iexact = 'ME')):
            d['percentage_delivery_at_home'] = ReportNSC.objects.filter(birth_location__location_category_designation__iexact = 'ME').count() / float(d['total_delivery']) * 100
        if(ReportNSC.objects.filter(birth_location__location_category_designation__iexact = 'RT')):
            d['percentage_delivery_on_road'] = ReportNSC.objects.filter(birth_location__location_category_designation__iexact = 'RT').count() / float(d['total_delivery']) * 100
        if(ReportNSC.objects.filter(birth_location__location_category_designation__iexact = 'CS')):
            d['percentage_delivery_at_CDS'] = ReportNSC.objects.filter(birth_location__location_category_designation__iexact = 'CS').count() / float(d['total_delivery']) * 100
        d['percentage_delivery_at_HF'] = d['percentage_delivery_at_CDS'] + d['percentage_delivery_at_hospital']


    #Statistics about VAC
    if(VAC.objects.all()):
        all_vac = VAC.objects.all()
        for v in all_vac:
            if(ReportVAC.objects.filter(vac = v)):
                number_of_such_reports = ReportVAC.objects.filter(vac = v).count()
                vac_designation = v.vac_designation
                new_object = {}
                new_object[vac_designation] = number_of_such_reports
                d['vac_list'].append(new_object)

    print(d['vac_list'])

    return render(request, 'home.html', d)


#require session
def communityhealthworker(request):
    d = {}
    d["pagetitle"] = "Community Health Worker"
    d['provinces'] = getprovinces()

    return render(request, 'communityhealthworker.html', d)


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

def getprovinces():
    return BPS.objects.all()


def getdistrictsinprovince(request):
    response_data = {}
    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        json_data = json.loads(request.body)
        code = json_data['code']
        if (code):
            districts = District.objects.filter(bps = BPS.objects.get(code = code))
            response_data = serializers.serialize('json', districts)
        return HttpResponse(response_data, content_type="application/json")


def getcdsindistrict(request):
    response_data = {}
    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        json_data = json.loads(request.body)
        code = json_data['code']
        if (code):
            cds = CDS.objects.filter(district = District.objects.get(code = code))
            response_data = serializers.serialize('json', cds)
        return HttpResponse(response_data, content_type="application/json")


def getcdsdata(request):
    response_data = {}
    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        json_data = json.loads(request.body)
        level = json_data['level']
        code = json_data['code']
        start_date = json_data['start_date']
        end_date = json_data['end_date']
        chwdata = ""

        if (level):
            cdslist = None
            if (level == "cds"):
                cdslist = CDS.objects.filter(code = code)

            elif (level == "district"):
                districtlist = District.objects.filter(code = code)
                if (districtlist):
                    cdslist = CDS.objects.filter(district__in = districtlist)
                
            elif (level == "province"):
                provincelist = BPS.objects.filter(code = code)
                if (provincelist):
                    districtlist = District.objects.filter(bps__in = provincelist)
                    if (districtlist):
                        cdslist = CDS.objects.filter(district__in = districtlist)

            if (cdslist):
                chwdata = CHW.objects.filter(cds__in = cdslist).filter(reg_date__range=[start_date, end_date]).order_by('reg_date')

            response_data = serializers.serialize('json', chwdata)

        return HttpResponse(response_data, content_type="application/json")

        