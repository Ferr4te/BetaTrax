from django.contrib import admin
from .models import Product, ProductOwner, Developer, BetaTester, DefectReport

# Register your models here.
admin.site.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id',)

admin.site.register(ProductOwner)
class ProductOwnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'product')

admin.site.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ('id', 'product')
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    
    def get_fixed_count(self, obj):
        metrics = obj.get_effectiveness_metrics()
        return metrics['fixed_count']
    get_fixed_count.short_description = 'Total Fixed'
    
    def get_reopened_count(self, obj):
        metrics = obj.get_effectiveness_metrics()
        return metrics['reopened_count']
    get_reopened_count.short_description = 'Total Reopened'
    
    def get_effectiveness_rating(self, obj):
        metrics = obj.get_effectiveness_metrics()
        return metrics['classification']
    get_effectiveness_rating.short_description = 'Effectiveness'

admin.site.register(BetaTester)
class BetaTesterAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')

admin.site.register(DefectReport)
class DefectReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'severity', 'priority', 'product', 'betatester', 'developer')
    list_filter = ('status', 'severity', 'priority')
    search_fields = ('title', 'description')
