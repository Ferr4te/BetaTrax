from django import forms

class DefectForm(forms.Form):
    testerid = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=254, required=False)
    version = forms.CharField()
    title = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea)
    reproduce_step = forms.CharField(widget=forms.Textarea)
    defect_date_time = forms.DateTimeField(required=False)
