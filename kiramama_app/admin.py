# -*- coding: utf-8 -*-
from django.contrib import admin
from kiramama_app.models import *
from import_export import resources
from import_export.admin import ExportMixin


class ReportNSCResource(resources.ModelResource):
    class Meta:
        model = ReportNSC
        fields = (
            "report",
            "child_number",
            "birth_date",
            "birth_location",
            "gender",
            "weight",
            "next_appointment_date",
            "breast_feading",
        )


class ReportNSCAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ReportNSCResource
    search_fields = ("child_number", "birth_location", "breast_feading")
    list_display = (
        "id",
        "birth_date",
        "birth_location",
        "child_number",
        "mother",
        "sex",
        "weight",
        "breast_feading",
    )
    date_hierarchy = "birth_date"
    list_filter = ("gender", "birth_location", "child_number", "breast_feading")

    def mother(self, obj):
        return obj.report.mother.id_mother

    def sex(self, obj):
        return obj.gender.gender_code


class CHWAdmin(admin.ModelAdmin):
    actions = ["download_csv"]
    list_display = [
        "phone_number",
        "supervisor_phone_number",
        "get_cds_name",
        "get_cds_code",
        "get_sub_colline",
        "get_colline",
        "get_district_name",
        "get_bps_name",
    ]

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

    get_cds_name.admin_order_field = "cds__name"
    get_cds_code.admin_order_field = "cds__code"
    get_sub_colline.admin_order_field = "sub_colline__name"
    get_colline.admin_order_field = "sub_colline__colline__name"
    get_district_name.admin_order_field = "cds__district"
    get_bps_name.admin_order_field = "cds__district__bps"

    list_filter = ("cds__district", "cds__district__bps")

    def download_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        import StringIO

        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(
            [
                "CHW Phone Number",
                "Supervisor Phone Number",
                "CDS Name",
                "CDS Code",
                "Sub Colline",
                "Colline",
                "District",
                "BPS",
            ]
        )

        for s in queryset:
            print type(s.cds.code)
            writer.writerow(
                [
                    s.phone_number,
                    s.supervisor_phone_number,
                    s.cds.name.encode("utf-8"),
                    s.cds.code,
                    s.sub_colline,
                    s.sub_colline.colline,
                    s.cds.district,
                    s.cds.district.bps,
                ]
            )

        f.seek(0)

        response = HttpResponse(f, content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=chws.csv"
        return response

    download_csv.short_description = "Download"


class ReportRISAdmin(admin.ModelAdmin):
    actions = ["download_csv"]
    list_display = [
        "report",
        "get_report_date",
        "mother_arrived_at_health_facility",
        "get_cds_code",
        "get_sub_colline",
        "get_colline",
        "get_district_name",
        "get_bps_name",
    ]

    def report(self, obj):
        return obj.report

    def get_report_date(self, obj):
        return obj.report.reporting_date

    def mother_arrived_at_health_facility(self, obj):
        return obj.mother_arrived_at_health_facility

    """def get_cds_name(self, obj):
        return obj.report.cds.name"""

    def get_cds_code(self, obj):
        return obj.report.cds.code

    def get_sub_colline(self, obj):
        return obj.report.sub_hill.name

    def get_colline(self, obj):
        return obj.report.sub_hill.colline.name

    def get_district_name(self, obj):
        return obj.report.cds.district.name

    def get_bps_name(self, obj):
        return obj.report.cds.district.bps.name

    report.short_description = "Report"
    get_report_date.short_description = "Reporting date"
    mother_arrived_at_health_facility.short_description = "Woman arrived at HF"
    # get_cds_name.short_description = "CDS name"
    get_cds_code.short_description = "CDS code"
    get_sub_colline.short_description = "Sub colline"
    get_colline.short_description = "Colline"
    get_district_name.short_description = "District"
    get_bps_name.short_description = "BPS"

    list_filter = (
        "mother_arrived_at_health_facility",
        "report__cds__district__bps",
        "report__cds__district",
    )

    def download_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        import StringIO

        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(
            [
                "Report",
                "Reporting date",
                "Woman arrived at HF",
                "CDS Code",
                "Sub colline",
                "Colline",
                "District",
                "BPS",
            ]
        )

        for s in queryset:
            print type(s.report)
            writer.writerow(
                [
                    s.report,
                    s.report.reporting_date,
                    s.mother_arrived_at_health_facility,
                    s.report.cds.code,
                    s.report.sub_hill.name,
                    s.report.sub_hill.colline.name,
                    s.report.cds.district.name,
                    s.report.cds.district.bps.name,
                ]
            )

        f.seek(0)

        response = HttpResponse(f, content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=Risk_reports.csv"
        return response

    download_csv.short_description = "Download"


class ReportAdmin(admin.ModelAdmin):
    actions = ["download_csv"]
    date_hierarchy = "reporting_date"
    list_display = [
        "report_category",
        "text",
        "get_report_date",
        "get_cds_code",
        "get_sub_colline",
        "get_colline",
        "get_district_name",
        "get_bps_name",
    ]

    def report_category(self, obj):
        return obj.category

    def text(self, obj):
        return obj.text

    def get_report_date(self, obj):
        return obj.reporting_date

    def get_cds_code(self, obj):
        return obj.cds.code

    def get_sub_colline(self, obj):
        return obj.sub_hill.name

    def get_colline(self, obj):
        return obj.sub_hill.colline.name

    def get_district_name(self, obj):
        return obj.cds.district.name

    def get_bps_name(self, obj):
        return obj.cds.district.bps.name

    report_category.short_description = "Report category"
    text.short_description = "Sent text"
    get_report_date.short_description = "Reporting date"
    get_cds_code.short_description = "CDS code"
    get_sub_colline.short_description = "Sub colline"
    get_colline.short_description = "Colline"
    get_district_name.short_description = "District"
    get_bps_name.short_description = "BPS"

    list_filter = ("category", "cds__district__bps", "cds__district")

    def download_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        import StringIO

        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(
            [
                "Report category",
                "Sent text",
                "Reporting date",
                "CDS Code",
                "Sub colline",
                "Colline",
                "District",
                "BPS",
            ]
        )

        for s in queryset:
            print type(s.text)
            writer.writerow(
                [
                    s.category,
                    s.text,
                    s.reporting_date,
                    s.cds.code,
                    s.sub_hill.name,
                    s.sub_hill.colline.name,
                    s.cds.district.name,
                    s.cds.district.bps.name,
                ]
            )

        f.seek(0)

        response = HttpResponse(f, content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=Reports.csv"
        return response

    download_csv.short_description = "Download"


class NotificationsCHWAdmin(admin.ModelAdmin):
    actions = ["download_csv"]
    list_display = [
        "chw",
        "get_message_to_send",
        "get_date_for_sending",
        "get_bps_name",
        "get_district_name",
    ]

    def chw(self, obj):
        return obj.chw

    def get_message_to_send(self, obj):
        return obj.message_to_send

    def get_date_for_sending(self, obj):
        return obj.date_time_for_sending

    def get_bps_name(self, obj):
        return obj.chw.cds.district.bps.name

    def get_district_name(self, obj):
        return obj.chw.cds.district.name

    chw.short_description = "CHW"
    get_message_to_send.short_description = "Message"
    get_date_for_sending.short_description = "Send date"
    get_bps_name.short_description = "Province"
    get_district_name.short_description = "District"

    list_filter = ("chw__cds__district__bps", "chw__cds__district")

    def download_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        import StringIO

        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(["CHW", "Message", "Send date", "Province", "District"])

        for s in queryset:
            print type(s.chw)
            writer.writerow(
                [
                    s.chw,
                    s.message_to_send,
                    s.date_time_for_sending,
                    s.chw.cds.district.bps.name,
                    s.chw.cds.district.name,
                ]
            )

        f.seek(0)

        response = HttpResponse(f, content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=Reminders.csv"
        return response

    download_csv.short_description = "Download"


class MotherAdmin(admin.ModelAdmin):
    actions = ["download_csv"]
    list_display = [
        "id_mother",
        "phone_number",
    ]

    def get_id_mother(self, obj):
        return obj.id_mother

    def get_phone_number(self, obj):
        return obj.phone_number

    get_id_mother.short_description = "Mother ID"
    get_phone_number.short_description = "Phone number"

    #list_filter = ("id_mother", "phone_number")

    def download_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        import StringIO

        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(
            [
                "Mother ID",
                "Phone number",
            ]
        )

        for s in queryset:
            writer.writerow(
                [
                    s.id_mother,
                    s.phone_number,
                ]
            )

        f.seek(0)

        response = HttpResponse(f, content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=Mothers.csv"
        return response

    download_csv.short_description = "Download"

admin.site.register(CHW, CHWAdmin)
admin.site.register(Mother, MotherAdmin)
admin.site.register(Report, ReportAdmin)
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
admin.site.register(NotificationsCHW, NotificationsCHWAdmin)
admin.site.register(Settings)
admin.site.register(AllSupervisor)
admin.site.register(DistrictSupervisor)
#admin.site.register(ProvinceSupervisor)
admin.site.register(BPSSupervisor)
admin.site.register(CDSSupervisor)

admin.site.register(ReportPriseC)
admin.site.register(ReportResponsePC)
admin.site.register(ReportMicroNTDistribution)
admin.site.register(ReportDepistage)
admin.site.register(MicronutrientIntake)
admin.site.register(Time)
