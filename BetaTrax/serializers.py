from rest_framework import serializers
from .models import DefectReport

#PBI-01
class DefectReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReport
        exclude = ['status', 'severity', 'priority', 'productowner', 'developer']


#PBI-02 + PBI-08
class EvaluateDefectSerializer(serializers.ModelSerializer):
    # allow sending the id of the original defect
    duplicate_of = serializers.PrimaryKeyRelatedField(
        queryset=DefectReport.objects.all(),
        required=False,
        allow_null=True,
    )
    class Meta:
        model = DefectReport
        fields = ['id', 'title', 'description', 'reproduce_step', 'version', 
                  'tester_email', 'status', 'severity', 'priority','duplicate_of']
        read_only_fields = ['id', 'title', 'description', 'reproduce_step', 
                           'version', 'tester_email']

    def validate(self, attrs):
        defect = self.instance  
        duplicate_of = attrs.get('duplicate_of')
        # If marking as duplicated, duplicate_of must be provided
        if attrs.get('status') == DefectReport.CurrentStatus.DUPLICATED:
            if not duplicate_of:
                raise serializers.ValidationError(
                    {'duplicate_of': 'You must specify the original defect this duplicates.'}
                )
            if duplicate_of.id == defect.id:
                raise serializers.ValidationError(
                    {'duplicate_of': 'A defect cannot be a duplicate of itself.'}
                )
            #  Enforce same product
            if duplicate_of.product_id != defect.product_id:
                raise serializers.ValidationError(
                    {'duplicate_of': 'Duplicate must refer to a defect from the same product.'}
                )
        return attrs

#PBI-04 and PBI-05
class DefectReportReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReport
        fields = '__all__'
