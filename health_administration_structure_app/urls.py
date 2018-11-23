from health_administration_structure_app.views import (
    BPSViewset,
    DistrictViewset,
    CDSViewset,
)
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r"provinces", BPSViewset)
router.register(r"districts", DistrictViewset)
router.register(r"cds", CDSViewset)
urlpatterns = router.urls
