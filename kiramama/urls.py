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
from django.contrib import admin
import kiramama_app.views
'''
urlpatterns = [
    url(r'^admin/', admin.site.urls),
]'''
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^kiramama/', include('kiramama_app.urls')),
    url(r'^$', kiramama_app.views.default, name='default'),
    url(r'^home', kiramama_app.views.home, name='home'),
    url(r'^communityhealthworker', kiramama_app.views.communityhealthworker, name='communityhealthworker'),
    url(r'^maternalhealth', kiramama_app.views.maternalhealth, name='maternalhealth'),
    url(r'^childhealth', kiramama_app.views.childhealth, name='childhealth'),
    url(r'^login', kiramama_app.views.login, name='login'),
    url(r'^logout', kiramama_app.views.logout, name='logout'),
    
    ]
