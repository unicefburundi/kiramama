"""kiramama URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
import kiramama_app.views
from django.contrib.auth import views as auth_views
'''
urlpatterns = [
    url(r'^admin/', admin.site.urls),
]'''

#urlpatterns = i18n_patterns (
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^kiramama/', include('kiramama_app.urls')),
    url(r'^structures/', include('health_administration_structure_app.urls')),
    url(r'^home/vaccination_reports/(?P<vac>)$', kiramama_app.views.vaccination_reports, name='vaccination_reports'),
    url(r'^home/vaccination_reports/mother_details/(?P<child>)', kiramama_app.views.mother_details, name='mother_details'),
    url(r'^home/$', kiramama_app.views.home, name='home'),
    url(r'^communityhealthworker', kiramama_app.views.communityhealthworker, name='communityhealthworker'),

    url(r'^maternalhealth', kiramama_app.views.maternalhealth, name='maternalhealth'),
    url(r'^births', kiramama_app.views.births, name='births'),
    url(r'^risks', kiramama_app.views.risks, name='risks'),
    url(r'^red_alerts', kiramama_app.views.red_alerts, name='red_alerts'),
    url(r'^deaths', kiramama_app.views.deaths, name='deaths'),
    url(r'^reminders', kiramama_app.views.reminders, name='reminders'),

    url(r'^childhealth', kiramama_app.views.childhealth, name='childhealth'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^getdistrictsinprovince', kiramama_app.views.getdistrictsinprovince, name='getdistrictsinprovince'),
    url(r'^getcdsindistrict', kiramama_app.views.getcdsindistrict, name='getcdsindistrict'),
    url(r'^getcdsdata', kiramama_app.views.getcdsdata, name='getcdsdata'),
    
    url(r'^getwanteddata', kiramama_app.views.getwanteddata, name='getwanteddata'),
    url(r'^get_births_data', kiramama_app.views.get_births_data, name='get_births_data'),
    url(r'^get_risks_data', kiramama_app.views.get_risks_data, name='get_risks_data'),
    url(r'^get_red_alerts_data', kiramama_app.views.get_red_alerts_data, name='get_red_alerts_data'),
    url(r'^get_deaths_data', kiramama_app.views.get_deaths_data, name='get_deaths_data'),
    url(r'^get_reminders$', kiramama_app.views.get_reminders, name='get_reminders'),

    url(r'^get_child_health_data', kiramama_app.views.get_child_health_data, name='get_child_health_data'),
    url(r'^$', kiramama_app.views.default, name='default'),


    url(r'^registered_preg_details/(?P<location_name>)$', kiramama_app.views.registered_preg_details, name='registered_preg_details'),
    url(r'^registered_risk_details/(?P<location_name>)$', kiramama_app.views.registered_risk_details, name='registered_risk_details'),
    url(r'^red_alerts_details/(?P<location_name>)$', kiramama_app.views.red_alerts_details, name='red_alerts_details'),
    url(r'^registered_deaths_details/(?P<location_name>)$', kiramama_app.views.registered_deaths_details, name='registered_deaths_details'),
    url(r'^reminder_details/(?P<location_name>)$', kiramama_app.views.reminder_details, name='reminder_details'),


    url(r'^mother_message_history/(?P<mother_id>)', kiramama_app.views.mother_message_history, name='mother_message_history'),
    url(r'^child_message_history/(?P<child_id>)', kiramama_app.views.child_message_history, name='child_message_history'),
    url(r'^home/active_chw', kiramama_app.views.active_chw, name='active_chw'),
    url(r'^home/inactive_chw', kiramama_app.views.inactive_chw, name='inactive_chw'),
    url(r'^h_r_registered_preg_details/(?P<location_name>)$', kiramama_app.views.h_r_registered_preg_details, name='h_r_registered_preg_details'),
    url(r'^expected_delivery_details/(?P<location_name>)$', kiramama_app.views.expected_delivery_details, name='expected_delivery_details'),
    url(r'^hr_expected_delivery_details/(?P<location_name>)$', kiramama_app.views.hr_expected_delivery_details, name='hr_expected_delivery_details'),
    url(r'^p_w_s_e_d_details/(?P<location_name>)$', kiramama_app.views.p_w_s_e_d_details, name='p_w_s_e_d_details'),
    url(r'^p_w_e_d_next_2_w_details/(?P<location_name>)$', kiramama_app.views.p_w_e_d_next_2_w_details, name='p_w_e_d_next_2_w_details'),
    url(r'^h_r_p_w_e_d_next_2_w_details/(?P<location_name>)$', kiramama_app.views.h_r_p_w_e_d_next_2_w_details, name='h_r_p_w_e_d_next_2_w_details'),
    url(r'^registered_births_details/(?P<location_name>)$', kiramama_app.views.registered_births_details, name='registered_births_details'),
    url(r'^home_births_details/(?P<location_name>)$', kiramama_app.views.home_births_details, name='home_births_details'),
    url(r'^road_births_details/(?P<location_name>)$', kiramama_app.views.road_births_details, name='road_births_details'),
    url(r'^health_facility_births_details/(?P<location_name>)$', kiramama_app.views.health_facility_births_details, name='health_facility_births_details'),
    url(r'^breastf_in_first_hour_details/(?P<location_name>)$', kiramama_app.views.breastf_in_first_hour_details, name='breastf_in_first_hour_details'),
    url(r'^breastf_after_first_hour_details/(?P<location_name>)$', kiramama_app.views.breastf_after_first_hour_details, name='breastf_after_first_hour_details'),
]
#   )

