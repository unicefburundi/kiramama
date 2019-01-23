# -*- coding: utf-8 -*-
from rest_framework import serializers
from health_administration_structure_app.models import BPS, District, CDS


class BPSSerializer(serializers.ModelSerializer):

    class Meta:
        model = BPS
        fields = ('code', 'name', )


class DistrictSerializer(serializers.ModelSerializer):

    class Meta:
        model = District
        fields = ('code', 'name', 'bps', )


class CDSSerializer(serializers.ModelSerializer):

    class Meta:
        model = CDS
        fields = ('code', 'name', 'district', )
