from django import forms
from django.forms import ModelForm
from .models import Cargo, cargoList


vehicles = [
        (600,'MPV (600 kg)'),
        (1000,'Small truck (1000 kg)'),
        (2000,'Large truck (2000 kg)'),
    ]

class generateForm(ModelForm):
    class Meta:
        model = Cargo
        fields = ['num_box','capacity','ini_rate']
        widgets = {
            'num_box' : forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"10","max":"500"}),
            'capacity' : forms.Select(choices=vehicles),
            'ini_rate' : forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"5","step":"0.01"}),
        }
    
class uploadCSV(forms.Form):
    capacity = forms.IntegerField(widget=forms.Select(choices=vehicles))
    ini_rate = forms.DecimalField(widget=forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"5","step":"0.01"}),)
    csvFile = forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv"}))
   
class cargoForm(ModelForm):
    class Meta:
        model = cargoList
        fields = ['description','height','length','width','weight']
        widgets = {
            'description' : forms.TextInput(attrs={'placeholder':'---'}),
            'height' : forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"*","step":"0.01"}),
            'length' : forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"*","step":"0.01"}),
            'width' : forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"*","step":"0.01"}),
            'weight' : forms.TextInput(attrs={'min':'0','type':'number',"placeholder":"*","step":"0.01"}),
        }
        