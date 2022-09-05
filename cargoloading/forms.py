from email.policy import default
from django import forms
from .models import *

class generateForm(forms.Form):
    vehicles = [
        (600,'MPV (600 kg)'),
        (1000,'Small truck (1000 kg)'),
        (2000,'Large truck (2000 kg)'),
    ]

    num_box = forms.IntegerField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"10"}))
    capacity = forms.IntegerField(widget=forms.Select(choices=vehicles))
    ini_rate = forms.DecimalField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"5","step":"0.01"}),)
    cargo_type = forms.CharField(widget=forms.TextInput(attrs={'type':'text','placeholder':'Type of goods'}), max_length=120, required=True)

class tableForm(forms.Form):
    description = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'---'}), max_length=100, required=False)
    height = forms.FloatField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"*","step":"0.01"}),)
    length = forms.FloatField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"*","step":"0.01"}),)
    width = forms.FloatField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"*","step":"0.01"}),)
    weight = forms.FloatField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"*","step":"0.01"}),)