from rest_framework import serializers
from .models import DefectReport

#PBI-01
class DefectReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReport
        exclude = ['status', 'severity', 'priority', 'productowner', 'developer']

#PBI-02
class EvaluateDefectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReport
        fields = ['id', 'title', 'description', 'reproduce_step', 'version', 
                  'tester_email', 'status', 'severity', 'priority']
        read_only_fields = ['id', 'title', 'description', 'reproduce_step', 
                           'version', 'tester_email']

#PBI-04 and PBI-05
class DefectReportReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReport
        fields = '__all__'
