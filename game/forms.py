from django import forms
from game.models import GameServer


class GameBrowser(forms.Form):

    servers = GameServer.objects.all()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(-1, 'All')]
        for server in self.servers:
            choices.append((server.id, server.hostname_plain))
        self.fields['server'].choices = choices

    start = forms.DateTimeField(label='Start time', required=False,\
        widget=forms.DateInput(attrs={'type': 'date'})\
        )
    end = forms.DateTimeField(label='End time', required=False,\
        widget=forms.DateInput(attrs={'type': 'date'})\
        )
    server = forms.TypedChoiceField(label='Server', required=False,\
        coerce=int, empty_value=-1\
        )
    submit_label = 'browse'

class StatisticsFilter(forms.Form):
    start = forms.DateTimeField(label='Start time', required=False,\
        widget=forms.DateInput(attrs={'type': 'date'})\
        )
    end = forms.DateTimeField(label='End time', required=False,\
        widget=forms.DateInput(attrs={'type': 'date'})\
        )
    submit_label = 'filter'
