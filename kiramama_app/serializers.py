# -*- coding: utf-8 -*-
from rest_framework import serializers
from kiramama_app.models import ReportNSC


class NSCSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    mother_id = serializers.SerializerMethodField()
    breast_feading = serializers.SerializerMethodField()
    birth_location = serializers.SerializerMethodField()

    class Meta:
        model = ReportNSC
        fields = (
            "id",
            "report",
            "child_number",
            "birth_date",
            "birth_location",
            "gender",
            "weight",
            "mother_id",
            "breast_feading",
        )

    def get_gender(self, obj):
        return obj.gender.gender_code

    def get_mother_id(self, obj):
        return obj.report.mother.id_mother

    def get_breast_feading(self, obj):
        return obj.breast_feading.breast_feed_option_description

    def get_birth_location(self, obj):
        return obj.birth_location.location_category_designation
