from django.conf.urls import url
from kiramama_app.backend import handel_rapidpro_request
from kiramama_app.views import *


urlpatterns = [
    url(r'external_request', handel_rapidpro_request, name="handel_request"),
    #url(r'^$', home, name="home"),
]
