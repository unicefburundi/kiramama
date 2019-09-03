from django.conf.urls import url, include
from kiramama_app.backend import handel_rapidpro_request
from kiramama_app.views import *
from rest_framework import routers
from kiramama_app.tasks import send_scheduled_sms


router = routers.DefaultRouter()
router.register(r"reportnsc", ReportNSCViewsets)


urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"external_request", handel_rapidpro_request, name="handel_request"),
    url(r"send_scheduled_sms", send_scheduled_sms, name="send_scheduled_sms"),
    url(r"^mother/(?P<slug>\w+)/$", MotherDetailView.as_view(), name="mother-details"),
]
