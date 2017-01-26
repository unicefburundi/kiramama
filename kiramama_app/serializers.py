from rest_framework import serializers
from kiramama_app.models import ReportNSC


class NSCSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportNSC
        fields = ('report', 'child_number', 'birth_date', 'birth_location', 'gender', 'weight', 'next_appointment_date', 'breast_feading' )
