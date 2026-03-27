from django.db import models

# Create your models here.
class Product(models.Model):
    pass

class ProductOwner(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class Developer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class BetaTester(models.Model):
    email=models.CharField(max_length=254)

class DefectReport(models.Model):
    version=models.IntegerField()
    title=models.TextField()
    description=models.TextField()
    reproduce_step=models.TextField()
    defect_date_time=models.TimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=CurrentStatus.choices, default=CurrentStatus.NEW)
    severity = models.CharField(max_length=10, choices=Severity.choices, null=TRUE, blank=TRUE)
    priority = models.CharField(max_length=10, choices=Priority.choices, null=TRUE, blank=TRUE)
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    betatester = models.ForeignKey(BetaTester, on_delete=models.CASCADE)
    productowner = models.ForeignKey(ProductOwner, on_delete=models.CASCADE)
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)

    class CurrentStatus(models.TextChoices):
        NEW              = 'New',              'New'
        OPEN             = 'Open',             'Open'
        ASSIGNED         = 'Assigned',         'Assigned'
        CANNOT_REPRODUCE = 'CannotReproduce',  'Cannot Reproduce'
        FIXED            = 'Fixed',            'Fixed'
        REOPENED         = 'Reopened',          'Reopened'
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
