from django import forms
from .models import Stock, Company


class MainForm(forms.Form):
    min_percentage_increase = forms.DecimalField(widget=forms.DateInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    max_percentage_increase = forms.DecimalField(widget=forms.DateInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    minimum_volume = forms.DecimalField(label=' Minimum volume (in millions)', widget=forms.DateInput(attrs={'class': 'form-control', 'autocomplete':'off'}))
    maximum_volume = forms.DecimalField(label=' Maximum volume (in millions)', widget=forms.DateInput(attrs={'class': 'form-control', 'autocomplete':'off'}))
    start_date = forms.CharField(widget=forms.DateInput(attrs={'class': 'date_form_input form-control'}))
    end_date = forms.CharField(widget=forms.DateInput(attrs={'class': 'date_form_input form-control'}))
