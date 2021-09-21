from django import forms

class GameBrowser(forms.Form):
    start = forms.DateTimeField(label='Start time',
        widget=forms.DateInput(attrs={'type': 'date'}))
    end = forms.DateField(label='End time', 
        widget=forms.DateInput(attrs={'type': 'date'}))
