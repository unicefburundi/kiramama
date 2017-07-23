# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from kiramama_app.models import *
from health_administration_structure_app.models import *
from django.utils.translation import ugettext as _
import datetime
import json
from django.core import serializers
from django.contrib.auth.decorators import login_required
from kiramama_app.serializers import NSCSerializer
from rest_framework import viewsets
import django_filters
from django.views.generic import DetailView
import unicodedata
import ast


def default(request):
    d = {}
    return render(request, 'default.html', d)


@login_required
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

    if (CPN.objects.filter(cpn_designation="CPN1")):
        cpn1 = CPN.objects.get(cpn_designation="CPN1")
    if(CPN.objects.filter(cpn_designation="CPN2")):
        cpn2 = CPN.objects.get(cpn_designation="CPN2")
    if(CPN.objects.filter(cpn_designation="CPN3")):
        cpn3 = CPN.objects.get(cpn_designation="CPN3")
    if(CPN.objects.filter(cpn_designation="CPN4")):
        cpn4 = CPN.objects.get(cpn_designation="CPN4")

    if (cpn1):
        d['cpn1'] = float(ReportCPN.objects.filter(concerned_cpn=cpn1).count())/ float(cpntotal) * 100.0

    if (cpn2):
        d['cpn2'] = float(ReportCPN.objects.filter(concerned_cpn=cpn2).count())/ float(cpntotal) * 100.0

    if (cpn3):
        d['cpn3'] = float(ReportCPN.objects.filter(concerned_cpn=cpn3).count())/ float(cpntotal) * 100.0

    if (cpn4):
        d['cpn4'] = float(ReportCPN.objects.filter(concerned_cpn=cpn4).count())/ float(cpntotal) * 100.0

    # What is the percentage of active and inactive CHWs
    if(CHW.objects.all()):
        d['number_of_chw'] = CHW.objects.count()

        if(CHW.objects.filter(is_active=True)):
            d['percentage_of_active_chw'] = CHW.objects.filter(is_active=True).count() / float(d['number_of_chw']) * 100

        if(CHW.objects.filter(is_active=False)):
            d['percentage_of_not_active_chw'] = CHW.objects.filter(is_active=False).count() / float(d['number_of_chw']) * 100

    # Statistics about delivery
    if(ReportNSC.objects.all()):
        d['total_delivery'] = ReportNSC.objects.count()
        if(ReportNSC.objects.filter(birth_location__location_category_designation__iexact='HP')):
            d['percentage_delivery_at_hospital'] = ReportNSC.objects.filter(birth_location__location_category_designation__iexact='HP').count() / float(d['total_delivery']) * 100
        if(ReportNSC.objects.filter(birth_location__location_category_designation__iexact='ME')):
            d['percentage_delivery_at_home'] = ReportNSC.objects.filter(birth_location__location_category_designation__iexact='ME').count() / float(d['total_delivery']) * 100
        if(ReportNSC.objects.filter(birth_location__location_category_designation__iexact='RT')):
            d['percentage_delivery_on_road'] = ReportNSC.objects.filter(birth_location__location_category_designation__iexact='RT').count() / float(d['total_delivery']) * 100
        if(ReportNSC.objects.filter(birth_location__location_category_designation__iexact='CS')):
            d['percentage_delivery_at_CDS'] = ReportNSC.objects.filter(birth_location__location_category_designation__iexact='CS').count() / float(d['total_delivery']) * 100
        d['percentage_delivery_at_HF'] = d['percentage_delivery_at_CDS'] + d['percentage_delivery_at_hospital']
        
    # Statistics about VAC
    new_object = {}
    all_vac = VAC.objects.all()
    if(all_vac):
        for v in all_vac:
            vac = ReportVAC.objects.filter(vac=v)
            if(vac):
                number_of_such_reports = vac.count()
                vac_designation = v.vac_designation
                new_object[vac_designation] = number_of_such_reports
            
    d['vac_list'] = new_object
    return render(request, 'home.html', d)


@login_required
def communityhealthworker(request):
    d = {}
    d["pagetitle"] = "Community Health Worker"
    d['provinces'] = getprovinces()

    return render(request, 'communityhealthworker.html', d)


@login_required
def maternalhealth(request):
    d = {}
    d["pagetitle"] = "Maternal Health"
    d['provinces'] = getprovinces()

    return render(request, 'maternalhealth.html', d)


@login_required
def childhealth(request):
    d = {}
    d["pagetitle"] = "Children Health"
    d['provinces'] = getprovinces()
    return render(request, 'childhealth.html', d)


def getprovinces():
    return BPS.objects.all()


def getdistrictsinprovince(request):
    response_data = {}
    if request.method == 'POST':
        # import pdb; pdb.set_trace()
        json_data = json.loads(request.body)
        code = json_data['code']
        if (code):
            districts = District.objects.filter(bps=BPS.objects.get(code=code))
            response_data = serializers.serialize('json', districts)
        return HttpResponse(response_data, content_type="application/json")


def getcdsindistrict(request):
    response_data = {}
    if request.method == 'POST':
        # import pdb; pdb.set_trace()
        json_data = json.loads(request.body)
        code = json_data['code']
        if (code):
            cds = CDS.objects.filter(district=District.objects.get(code=code))
            response_data = serializers.serialize('json', cds)
        return HttpResponse(response_data, content_type="application/json")


def getcdsdata(request):
    response_data = {}
    
    try:
        if request.method == 'POST':
            json_data = json.loads(request.body)
            level = json_data['level']
            code = json_data['code']
            start_date = json_data['start_date']
            end_date = json_data['end_date']
            chw_data = None
            #chwdata = cdsdata(level, code, start_date, end_date)

            if (level and code and start_date and end_date):
                cdslist = None
                if (level == "cds"):
                    cdslist = CDS.objects.filter(code=code)

                elif (level == "district"):
                    districtlist = District.objects.filter(code=code)
                    if (districtlist):
                        cdslist = CDS.objects.filter(district__in = districtlist)
                    
                elif (level == "province"):
                    provincelist = BPS.objects.filter(code = code)
                    if (provincelist):
                        districtlist = District.objects.filter(bps__in = provincelist)
                        if (districtlist):
                            cdslist = CDS.objects.filter(district__in = districtlist)

                if (cdslist):
                    chw_data = CHW.objects.filter(cds__in = cdslist).filter(reg_date__range=[start_date, end_date]).order_by('reg_date')

            else:
                chw_data = CHW.objects.all()
            
            response_data = serializers.serialize('json', chw_data)
            return HttpResponse(response_data, content_type="application/json")

        else:
            response_data = _("Method must be a POST")
            return HttpResponse(response_data)
            
    except Exception, e:
        response_data = _(e.message)
        return HttpResponse(response_data)


def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError


def getwanteddata(request):
    response_data = {}
    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        json_data = json.loads(request.body)
        level = json_data['level']
        code = json_data['code']
        start_date = json_data['start_date']
        end_date = json_data['end_date']
        grodata = ""
        all_data = []

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
            elif (level == "national"):
                cdslist = CDS.objects.all()

            if (cdslist):
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                new_start_date = start_date - datetime.timedelta(days=300)
                #Let fix start date to 10 months before the selected start date
                #grodata = ReportGRO.objects.filter(report__cds__in = cdslist).filter(report__reporting_date__range=[start_date, end_date])
                grodata = ReportGRO.objects.filter(report__cds__in = cdslist).filter(report__reporting_date__range=[new_start_date, end_date])

        gro_data_seri = serializers.serialize('python', grodata)
        columns = [g['fields'] for g in gro_data_seri]
        response_data = json.dumps(columns, default=date_handler)
        rows = json.loads(response_data)

        for r in rows:
            report = Report.objects.get(id = r['report'])
            r["cds_id"] = report.cds.id
            r["cds_name"] = report.cds.name
            r["district_id"] = report.cds.district.id
            r["district_name"] = report.cds.district.name
            r["bps_id"] = report.cds.district.bps.id
            r["bps_name"] = report.cds.district.bps.name
            r["reporting_date"] = report.reporting_date

            concerned_mother = report.mother

            if not (ReportNSC.objects.filter(report__mother = concerned_mother)):
                #This mother not yet reported as derivered
                r["derivered"] = False
                r["birth_date"] = ""
            else:
                r["derivered"] = True
                r["birth_date"] = ReportNSC.objects.filter(report__mother = concerned_mother)[0].birth_date

        rows = json.dumps(rows, default=date_handler)
        return HttpResponse(rows, content_type="application/json")


def vaccination_reports(request, vac):
    d = {}
    submited_vaccination_name = str(request.GET.get('vac', '')).strip()
    submited_vaccination = VAC.objects.filter(vac_designation = submited_vaccination_name)
    if(submited_vaccination):
        submited_vaccination = submited_vaccination[0]
        wanted_vaccination_reports = ReportVAC.objects.filter(vac=submited_vaccination)
        
        wanted_vaccination_reports = serializers.serialize('python', wanted_vaccination_reports)
        columns = [vr['fields'] for vr in wanted_vaccination_reports]
        wanted_vaccination_reports = json.dumps(columns, default=date_handler)
        wanted_vaccination_reports = json.loads(wanted_vaccination_reports)

        for r in wanted_vaccination_reports:
            l = Lieu.objects.filter(id = r['location'])
            if not (l):
                r["location name"] = ""
            else:
                r["location name"] = unicodedata.normalize('NFKD', l[0].location_category_designation).encode('ascii','ignore')
                #r["location name"] = l[0].location_category_designation

            nsc_id = r["child"]
            related_nsc = ReportNSC.objects.filter(id=nsc_id)
            if not (related_nsc):
                r["naissance_id"] = ""
            else:
                r["naissance_id"] = related_nsc[0].id

        if(wanted_vaccination_reports):
            d['selected_vaccination'] = submited_vaccination_name
            d['fetched_vaccination_reports'] = wanted_vaccination_reports
    return render(request, 'vaccination_reports.html', d)


def mother_details (request, child):
    submitted_child_id = str(request.GET.get('child', '')).strip()
    submitted_child_id = int(submitted_child_id)
    d = {}
    concerned_nsc = ReportNSC.objects.filter(id=submitted_child_id)
    if len(concerned_nsc) > 0:
        concerned_mother = concerned_nsc[0].report.mother
        d['mother_id'] = concerned_mother.id_mother
        d['phone_number'] = concerned_mother.phone_number
    return render(request, 'mother_details.html', d)


def registered_preg_details (request, location_name):
    #d = {}
    location_name = str(request.GET.get('location_name', '')).strip()
    location_level = str(request.GET.get('location_level', '')).strip()
    start_date = str(request.GET.get('start_date', '')).strip()
    end_date = str(request.GET.get('end_date', '')).strip()
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    
    if(location_level == "PROVINCE"):
        concerned_cdss = CDS.objects.filter(district__bps__name__iexact = location_name)
    if(location_level == "DISTRICT"):
        concerned_cdss = CDS.objects.filter(district__name__iexact = location_name)
    if(location_level == "CDS"):
        concerned_cdss = CDS.objects.filter(name__iexact = location_name)


    concerned_report_gro = ReportGRO.objects.filter(report__cds__in = concerned_cdss, report__reporting_date__range=[start_date, end_date])
    
    concerned_report_gro = serializers.serialize('python', concerned_report_gro)
    columns = [g['fields'] for g in concerned_report_gro]
    response_data = json.dumps(columns, default=date_handler)
    rows = json.loads(response_data)

    for r in rows:
        report = Report.objects.get(id = r['report'])
        r["sous_coline"] = report.sub_hill.name
        r["colline"] = report.sub_hill.colline.name
        r["commune"] = report.sub_hill.colline.commune.name
        r["province"] = report.sub_hill.colline.commune.province.name
        r["reporter_phone_number"] = report.chw.phone_number
        r["risk_level_name"] = RiskLevel.objects.get(id = r['risk_level']).risk_level_meaning
        r["lieu_de_consultation"] = Lieu.objects.get(id = r['consultation_location']).location_category_description


    return render(request, 'registered_pregnancies_details.html', {'rows':rows})



class NSCFilter(django_filters.rest_framework.FilterSet):
    min_birth_date = django_filters.DateFilter(name="birth_date", lookup_expr='gte')
    max_birth_date = django_filters.DateFilter(name="birth_date", lookup_expr='lte')
    cds = django_filters.CharFilter(name="report", lookup_expr='cds__code')
    district = django_filters.CharFilter(name="report", lookup_expr='cds__district__code')
    province = django_filters.CharFilter(name="report", lookup_expr='cds__district__bps__code')

    class Meta:
        model = ReportNSC
        fields = ['cds', 'district', 'province', 'min_birth_date', 'max_birth_date']


class ReportNSCViewsets(viewsets.ModelViewSet):
    serializer_class = NSCSerializer
    queryset = ReportNSC.objects.all()
    filter_class = NSCFilter
    filter_fields = ('report__cds__code', )


class MotherDetailView(DetailView):
    model = Mother
    template_name = "mother-detail.html"
    slug_field = 'id_mother'

    def get_context_data(self, **kwargs):
        context = super(MotherDetailView, self).get_context_data(**kwargs)
        return context

