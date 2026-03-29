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

class DefectReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReport
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']
