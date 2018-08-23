# -*- coding: utf-8 -*-
from django.contrib import admin
from public_administration_structure_app.models import *

admin.site.register(Province)
admin.site.register(Commune)
admin.site.register(Colline)
#admin.site.register(SousColline)

class SousCollineAdmin(admin.ModelAdmin):
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

admin.site.register(SousColline , SousCollineAdmin)
