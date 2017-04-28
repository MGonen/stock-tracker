from django import forms
from .models import Stock, Company


class MainForm(forms.Form):
    increase_percentage = forms.DecimalField(widget=forms.DateInput(attrs={'class': 'form-control'}))
    minimum_volume = forms.DecimalField(widget=forms.DateInput(attrs={'class': 'form-control'}))
    start_date = forms.CharField(widget=forms.DateInput(attrs={'class': 'date_form_input form-control'}))
    end_date = forms.CharField(widget=forms.DateInput(attrs={'class': 'date_form_input form-control'}))
