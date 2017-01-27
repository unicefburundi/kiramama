from health_administration_structure_app.models import BPS, District, CDS
from health_administration_structure_app.serializers import BPSSerializer, DistrictSerializer, CDSSerializer
from rest_framework import viewsets


class BPSViewset(viewsets.ModelViewSet):
    serializer_class = BPSSerializer
    queryset = BPS.objects.all()


class DistrictViewset(viewsets.ModelViewSet):
    serializer_class = DistrictSerializer
    queryset = District.objects.all()
    filter_fields = ('bps__code', )


class CDSViewset(viewsets.ModelViewSet):
    serializer_class = CDSSerializer
    queryset = CDS.objects.all()
    filter_fields = ('district__code', )
