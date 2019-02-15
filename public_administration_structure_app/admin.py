# -*- coding: utf-8 -*-
from django.contrib import admin
from public_administration_structure_app.models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class ProvinceResource(resources.ModelResource):
    class Meta:
        model = Province
        fields = ("id", "name", "code")


@admin.register(Province)
class ProvinceAdmin(ImportExportModelAdmin):
    resource_class = ProvinceResource
    search_fields = ("name", "code")
    list_display = ("name", "code")


class CommuneResource(resources.ModelResource):
    class Meta:
        model = Commune
        fields = ("id", "name", "code", "province__name", "province")


@admin.register(Commune)
class CommuneAdmin(ImportExportModelAdmin):
    resource_class = CommuneResource
    search_fields = ("name", "code")
    list_display = ("name", "code", "province")
    list_filter = ("province__name",)


class CollineResource(resources.ModelResource):
    class Meta:
        model = Colline
        fields = ("id", "name", "code", "commune__name", "commune__province__name")


@admin.register(Colline)
class CollineAdmin(ImportExportModelAdmin):
    resource_class = CollineResource
    search_fields = ("name", "code")
    list_display = ("name", "code", "commune", "province")
    list_filter = ("commune__province__name",)

    def province(self, obj):
        return obj.commune.province.name


class SousCollineAdmin(admin.ModelAdmin):
    actions = ["download_csv"]
    list_display = ["name", "get_colline_name", "get_commune_name", "get_province_name"]
    search_fields = ("name", "code")

    def get_colline_name(self, obj):
        return obj.colline.name

    def get_commune_name(self, obj):
        return obj.colline.commune.name

    def get_province_name(self, obj):
        return obj.colline.commune.province.name

    get_colline_name.short_description = "Colline"
    get_commune_name.short_description = "Commune"
    get_province_name.short_description = "Province"

    get_colline_name.admin_order_field = "colline"
    get_commune_name.admin_order_field = "colline__commune"
    get_province_name.admin_order_field = "colline__commune__province"

    list_filter = ("colline__commune__province", "colline__commune")

    def download_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        import StringIO

        f = StringIO.StringIO()
        writer = csv.writer(f)
        writer.writerow(["Name", "Colline", "Commune", "Province"])

        for s in queryset:
            writer.writerow(
                [s.name, s.colline, s.colline.commune, s.colline.commune.province]
            )

        f.seek(0)

        response = HttpResponse(f, content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=sub_collines.csv"
        return response

    download_csv.short_description = "Download"


admin.site.register(SousColline, SousCollineAdmin)
