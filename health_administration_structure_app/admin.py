from django.contrib import admin
from health_administration_structure_app.models import *
import csv
from django.http import HttpResponse
import StringIO

admin.site.register(BPS)
admin.site.register(District)
# admin.site.register(CDS)


class CDSAdmin(admin.ModelAdmin):
    actions = ["download_csv"]
    list_display = ["name", "code", "get_district_name", "get_bps_name"]

    def get_district_name(self, obj):
        return obj.district.name

    def get_bps_name(self, obj):
        return obj.district.bps.name

    get_district_name.short_description = "District"
    get_bps_name.short_description = "BPS"

    get_district_name.admin_order_field = "district"
    get_bps_name.admin_order_field = "district__bps"

    list_filter = ("district", "district__bps")

    def download_csv(self, request, queryset):

        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(["Name", "Code", "District", "BPS"])

        for s in queryset:
            writer.writerow(
                [s.name.encode("utf-8"), s.code, s.district, s.district.bps]
            )

        f.seek(0)

        response = HttpResponse(f, content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=cds_records.csv"
        return response

    download_csv.short_description = "Download"


admin.site.register(CDS, CDSAdmin)
