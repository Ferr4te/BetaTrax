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

admin.site.register(BetaTester)
class BetaTesterAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')

admin.site.register(DefectReport)
class DefectReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'severity', 'priority', 'product', 'betatester', 'developer')
    list_filter = ('status', 'severity', 'priority')
    search_fields = ('title', 'description')
