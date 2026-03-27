from django.db import models

# Create your models here.
class DefectReport(models.Model):
    report_id=models.IntegerField()
    version=models.IntegerField()
    title=models.TextField()
    description=models.TextField()
    reproduce_step=models.TextField()
    defect_date_time=models.TimeField(auto_now_add=True)

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

class ProductOwner(models.Model):
    product_owner_id=models.IntegerField()

class Product(models.Model):
    product_id=models.IntegerField()

class Developer(models.Model):
    developer_id=models.IntegerField()

class BetaTester(models.Model):
    tester_id=models.IntegerField()
    email=models.CharField()
