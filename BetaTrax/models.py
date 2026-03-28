from django.db import models

# Create your models here.
class Product(models.Model):
    def __str__(self):
        return (f"ProductID:{self.id}")

class ProductOwner(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    def __str__(self):
        return (f"ProductOwnerID:{self.id}")

class Developer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    def __str__(self):
        return (f"DeveloperID:{self.id}")

class BetaTester(models.Model):
    email=models.CharField(max_length=254)
    def __str__(self):
        return (f"BetaTesterID:{self.id}")

class DefectReport(models.Model):
    version=models.IntegerField()
    title=models.TextField()
    description=models.TextField()
    reproduce_step=models.TextField()
    defect_date_time=models.TimeField(auto_now_add=True)
    def __str__(self):
        return (f"DefectReportID:{self.id}")

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

    status = models.CharField(max_length=20, choices=CurrentStatus.choices, default=CurrentStatus.NEW)
    severity = models.CharField(max_length=10, choices=Severity.choices, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='defect_reports')
    betatester = models.ForeignKey(BetaTester, on_delete=models.CASCADE, related_name='defect_reports')
    productowner = models.ForeignKey(ProductOwner, on_delete=models.CASCADE, related_name='defect_reports')
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name='defect_reports')
