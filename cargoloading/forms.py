import csv, io, numbers
from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError
from .models import *

vehicles = [
        (600,'MPV (600 kg)'),
        (1000,'Small truck (1000 kg)'),
        (2000,'Large truck (2000 kg)'),
    ]

class generateForm(forms.Form):
    num_box = forms.IntegerField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"10"}))
    capacity = forms.IntegerField(widget=forms.Select(choices=vehicles))
    ini_rate = forms.DecimalField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"5","step":"0.01"}),)
    cargo_type = forms.CharField(widget=forms.TextInput(attrs={'type':'text','placeholder':'Type of goods'}), max_length=120, required=True)

#10 MB file size
MAX_UPLOAD_SIZE = "10485760"

class uploadCSV(forms.Form):
    cargo_type = forms.CharField(widget=forms.TextInput(attrs={'type':'text','placeholder':'Type of goods'}), max_length=120, required=True)
    capacity = forms.IntegerField(widget=forms.Select(choices=vehicles))
    ini_rate = forms.DecimalField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"5","step":"0.01"}),)
    csvFile = forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv"}))
    

    def validateFileData(self):
        file = self.cleaned_data['csvFile']
        data_set = file.read().decode('utf-8')
        print(data_set)
        set = io.StringIO(data_set)
        next(set)
        for d in csv.reader(set):
            print(type(d[1]))
            print(type(d[2]))
            print(type(d[3]))
            print(type(d[4]))
            

class tableForm(forms.Form):
    description = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'---'}), max_length=100, required=False)
    height = forms.FloatField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"*","step":"0.01"}),)
    length = forms.FloatField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"*","step":"0.01"}),)
    width = forms.FloatField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"*","step":"0.01"}),)
    weight = forms.FloatField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"*","step":"0.01"}),)