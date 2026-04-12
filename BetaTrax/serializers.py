from rest_framework import serializers
from .models import DefectReport, Product, Comment

#PBI-01
class DefectReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReport
        exclude = ['status', 'severity', 'priority', 'productowner', 'developer']


#PBI-02 + PBI-08 + PBI-07
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
        if attrs.get('status') == DefectReport.CurrentStatus.REJECTED:
            attrs['duplicate_of'] = None
        return attrs

#PBI-04 and PBI-05
class DefectReportReadOnlySerializer(serializers.ModelSerializer):

    #PBI-12 Add commnet field
    comments = serializers.SerializerMethodField()

    class Meta:
        model = DefectReport
        fields = '__all__'
    
    # PBI-12 Get comments
    def get_comments(self, obj):
        comments = obj.comments.all()
        return CommentSerializer(comments, many=True).data

# PBI-09 Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']
        extra_kwargs = {
            'name': {'required': True}
        }
    
    def validate_name(self, value):
        """Prevent duplicate product names (case-insensitive)"""
        if self.instance:
            if Product.objects.filter(name__iexact=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Product with this name already exists.")
        else:  # Creating new product
            if Product.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError("Product with this name already exists.")
        return value

# PBI-12 Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']
    
    def create(self, validated_data):
        """Automatically set author to current user"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
