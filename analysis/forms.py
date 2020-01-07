from django import forms
from . import models

#class DocumentForm(ModelForm):
#    class Meta:
#        model = models.Document
#        fields = ('upload_name', 'description', 'document',)


class UploadFileForm(forms.Form):
    file_field = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )

class DateRangeSelector(forms.Form):
    wells = forms.ModelMultipleChoiceField(
        queryset=models.Well.objects.all(),
        widget=forms.CheckboxSelectMultiple(), 
        required=True
    )
    start_date = forms.DateTimeField()
    end_date = forms.DateTimeField()
    units = forms.ModelMultipleChoiceField(
        queryset=models.Unit.objects.all(),
        widget=forms.CheckboxSelectMultiple(), 
        required=True
    )
