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
    url(r'^childhealth', kiramama_app.views.childhealth, name='childhealth'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^getdistrictsinprovince', kiramama_app.views.getdistrictsinprovince, name='getdistrictsinprovince'),
    url(r'^getcdsindistrict', kiramama_app.views.getcdsindistrict, name='getcdsindistrict'),
    url(r'^getcdsdata', kiramama_app.views.getcdsdata, name='getcdsdata'),
    url(r'^getwanteddata', kiramama_app.views.getwanteddata, name='getwanteddata'),
    url(r'^$', kiramama_app.views.default, name='default'),
    url(r'^registered_preg_details/(?P<location_name>)', kiramama_app.views.registered_preg_details, name='registered_preg_details'),

]
#   )

