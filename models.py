from django.db import models
from django.contrib.auth.models import User
from .developer_metrics import build_effectiveness_metrics

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=254, unique=True, null=True, blank=True)
    def __str__(self):
        return (f"ProductID:{self.id} - {self.name}" if self.name else f"ProductID:{self.id}")

class ProductOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='productowner')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    def __str__(self):
        return (f"ProductOwnerID:{self.id}")

class Developer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='developer')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    def __str__(self):
        return (f"DeveloperID:{self.id}")

    # PBI-18: Get effectiveness metrics for this developer
    def get_effectiveness_metrics(self):
        """
        Calculate effectiveness metrics for the developer.
        
        Returns:
            dict: Contains fixed_count, reopened_count, ratio, and classification
        """
        # Count defects fixed by this developer
        fixed_defects = DefectReport.objects.filter(
            developer=self,
            status=DefectReport.CurrentStatus.FIXED
        )
        fixed_count = fixed_defects.count()
        
        # Count defects reopened that were assigned to this developer
        # A defect is considered reopened if it has ever been in REOPENED status
        # and was assigned to this developer
        reopened_defects = DefectReport.objects.filter(
            developer=self,
            status=DefectReport.CurrentStatus.REOPENED
        )
        reopened_count = reopened_defects.count()
        
        return build_effectiveness_metrics(fixed_count=fixed_count, reopened_count=reopened_count)

class BetaTester(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='betatester')
    email = models.CharField(max_length=254)
    def __str__(self):
        return (f"BetaTesterID:{self.id}")

class DefectReport(models.Model):
    tester_email = models.CharField(max_length=254, blank=True, null=True)
    version=models.CharField(max_length=254)
    title=models.CharField(max_length=254)
    description=models.TextField()
    reproduce_step=models.TextField()
    defect_date_time=models.DateTimeField(auto_now_add=True)
    duplicate_of = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='duplicates',
        on_delete=models.CASCADE,
        help_text='If this defect is a duplicate, link to the original report.',
    )
    
    class CurrentStatus(models.TextChoices):
        NEW              = 'New',              'New'
        OPEN             = 'Open',             'Open'
        ASSIGNED         = 'Assigned',         'Assigned'
        CANNOT_REPRODUCE = 'CannotReproduce',  'Cannot Reproduce'
        FIXED            = 'Fixed',            'Fixed'
        REOPENED         = 'Reopened',         'Reopened'
        RESOLVED         = 'Resolved',         'Resolved'
        REJECTED         = 'Rejected',         'Rejected'
        DUPLICATED       = 'Duplicated',       'Duplicated'

    class Severity(models.TextChoices):
        CRITICAL = 'Critical', 'Critical'
        MAJOR    = 'Major',    'Major'
        MINOR    = 'Minor',    'Minor'
        LOW      = 'Low',      'Low'

    class Priority(models.TextChoices):
        CRITICAL = 'Critical', 'Critical'
        HIGH     = 'High',     'High'
        MEDIUM   = 'Medium',   'Medium'
        LOW      = 'Low',      'Low'

    status = models.CharField(max_length=64, choices=CurrentStatus.choices, default=CurrentStatus.NEW)
    severity = models.CharField(max_length=10, choices=Severity.choices, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, null=True, blank=True)

    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='defect_reports')
    betatester = models.ForeignKey(BetaTester,on_delete=models.CASCADE,related_name='defect_reports')
    productowner = models.ForeignKey(ProductOwner, on_delete=models.CASCADE,related_name='defect_reports', null=True, blank=True)
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name='defect_reports', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return (f"DefectReportID:{self.id}")
    
# PBI-12 Comment Model
class Comment(models.Model):
    defect = models.ForeignKey(DefectReport, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment on Defect {self.defect.id} by {self.author.username}"
