# -*- coding: utf-8 -*-
from django.contrib import admin
from public_administration_structure_app.models import *

admin.site.register(Province)
admin.site.register(Commune)
admin.site.register(Colline)
#admin.site.register(SousColline)

class SousCollineAdmin(admin.ModelAdmin):
	actions = ['download_csv']
	list_display = ['name', 'get_colline_name', 'get_commune_name', 'get_province_name']

	def get_colline_name(self, obj):
		return obj.colline.name
	def get_commune_name(self, obj):
		return obj.colline.commune.name
	def get_province_name(self, obj):
		return obj.colline.commune.province.name

	get_colline_name.short_description = "Colline"
	get_commune_name.short_description = "Commune"
	get_province_name.short_description = "Province"

	get_colline_name.admin_order_field = 'colline'
	get_commune_name.admin_order_field = 'colline__commune'
	get_province_name.admin_order_field = 'colline__commune__province'

	def download_csv(self, request, queryset):
		import csv
		from django.http import HttpResponse
		import StringIO

		f = StringIO.StringIO()
		writer = csv.writer(f)
		writer.writerow(["Name", "Colline", "Commune", "Province"])

		for s in queryset:
			writer.writerow([s.name, s.colline, s.colline.commune, s.colline.commune.province])

		f.seek(0)

		response = HttpResponse(f, content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=collines.csv'
		return response
	download_csv.short_description = "Download"

admin.site.register(SousColline , SousCollineAdmin)
