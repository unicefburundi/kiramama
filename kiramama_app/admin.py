# -*- coding: utf-8 -*-
from django.contrib import admin
from kiramama_app.models import *
from import_export import resources
from import_export.admin import ExportMixin


class ReportNSCResource(resources.ModelResource):
    class Meta:
        model = ReportNSC
        fields = ('report', 'child_number', 'birth_date', 'birth_location', 'gender', 'weight', 'next_appointment_date', 'breast_feading', )


class ReportNSCAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ReportNSCResource
    search_fields = ('child_number', 'birth_location', 'breast_feading', )
    list_display = ('id', 'birth_date', 'birth_location', 'child_number', 'mother', 'sex', 'weight', 'breast_feading', )
    date_hierarchy = 'birth_date'
    list_filter = ('gender', 'birth_location', 'child_number', 'breast_feading')

    def mother(self, obj):
        return obj.report.mother.id_mother

    def sex(self, obj):
        return obj.gender.gender_code


class CHWAdmin(admin.ModelAdmin):
    actions = ['download_csv']
    list_display = ['phone_number', 'supervisor_phone_number', 'get_cds_name', 'get_cds_code', 'get_sub_colline', 'get_colline', 'get_district_name', 'get_bps_name']

    def get_cds_name(self, obj):
        return obj.cds.name

    def get_cds_code(self, obj):
        return obj.cds.code

    def get_sub_colline(self, obj):
        return obj.sub_colline.name

    def get_colline(self, obj):
        return obj.sub_colline.colline.name

    def get_district_name(self, obj):
        return obj.cds.district.name

    def get_bps_name(self, obj):
        return obj.cds.district.bps.name

    get_cds_name.short_description = "CDS name"
    get_cds_code.short_description = "CDS code"
    get_sub_colline.short_description = "Sub colline"
    get_colline.short_description = "Colline"
    get_district_name.short_description = "District"
    get_bps_name.short_description = "BPS"

    get_cds_name.admin_order_field = 'cds__name'
    get_cds_code.admin_order_field = 'cds__code'
    get_sub_colline.admin_order_field = 'sub_colline__name'
    get_colline.admin_order_field = 'sub_colline__colline__name'
    get_district_name.admin_order_field = 'cds__district'
    get_bps_name.admin_order_field = 'cds__district__bps'

    list_filter = ("cds__district", "cds__district__bps",)

    def download_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        import StringIO

        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(["CHW Phone Number", "Supervisor Phone Number", "CDS Name", "CDS Code", "Sub Colline", "Colline", "District", "BPS"])

        for s in queryset:
            print type(s.cds.code)
            writer.writerow([s.phone_number, s.supervisor_phone_number, s.cds.name.encode('utf-8'), s.cds.code, s.sub_colline, s.sub_colline.colline, s.cds.district, s.cds.district.bps])

        f.seek(0)

        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=chws.csv'
        return response
    download_csv.short_description = "Download"




class ReportRISAdmin(admin.ModelAdmin):
    actions = ['download_csv']
    list_display = ['report', 'mother_arrived_at_health_facility']

    def report(self, obj):
        return obj.report

    def mother_arrived_at_health_facility(self, obj):
        return obj.mother_arrived_at_health_facility

    report.short_description = "Report"
    mother_arrived_at_health_facility.short_description = "Woman arrived at HF"

    list_filter = ("mother_arrived_at_health_facility",)

    def download_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        import StringIO

        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(["Report", "Woman arrived at HF"])

        for s in queryset:
            print type(s.report)
            writer.writerow([s.report, s.mother_arrived_at_health_facility])

        f.seek(0)

        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Risk_reports.csv'
        return response
    download_csv.short_description = "Download"


admin.site.register(CHW , CHWAdmin)
admin.site.register(Mother)
admin.site.register(Report)
admin.site.register(RiskLevel)
admin.site.register(Lieu)
admin.site.register(CPN)
admin.site.register(BreastFeed)
admin.site.register(CON)
admin.site.register(ChildNumber)
admin.site.register(Gender)
admin.site.register(VAC)
admin.site.register(Symptom)
admin.site.register(DeathCode)
admin.site.register(HealthStatus)
admin.site.register(Rescue)
admin.site.register(ReportGRO)
admin.site.register(ReportCPN)
admin.site.register(ReportNSC, ReportNSCAdmin)
admin.site.register(ReportCON)
admin.site.register(ReportVAC)
admin.site.register(ReportRIS, ReportRISAdmin)
admin.site.register(ReportRISBebe)
admin.site.register(ReportRER)
admin.site.register(ReportDEC)
admin.site.register(ReportDECBebe)
admin.site.register(ReportDEP)
admin.site.register(CON_Report_Symptom)
admin.site.register(CPN_Report_Symptom)
admin.site.register(RIS_Report_Symptom)
admin.site.register(Temporary)
admin.site.register(NotificationType)
admin.site.register(TimeMeasuringUnit)
admin.site.register(NotificationsForMother)
admin.site.register(NotificationsForCHW)
admin.site.register(NotificationsMother)
admin.site.register(NotificationsCHW)
admin.site.register(Settings)
admin.site.register(AllSupervisor)
admin.site.register(DistrictSupervisor)
admin.site.register(ProvinceSupervisor)