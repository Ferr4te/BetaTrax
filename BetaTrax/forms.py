from django import forms
from .models import DefectReport

class DefectForm(forms.ModelForm):
    class Meta:
        model = DefectReport
        fields = '__all__'
        exclude = ['status','severity','priority','productowner','developer']
