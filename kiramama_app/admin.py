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


admin.site.register(CHW)
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
admin.site.register(ReportRIS)
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
