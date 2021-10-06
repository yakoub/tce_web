from django import forms
from game.models import GameServer


class GameBrowser(forms.Form):
    submit_label = 'Filter'

    start = forms.DateTimeField(label='Start time', required=False,\
        widget=forms.DateInput(attrs={'type': 'date'})\
        )
    end = forms.DateTimeField(label='End time', required=False,\
        widget=forms.DateInput(attrs={'type': 'date'})\
        )

class StatisticsFilter(GameBrowser):
    exclude_bots = forms.BooleanField(label='Exclude bots',\
        required=False, initial=True)
    game = forms.TypedChoiceField(label='Game'\
        ,required=True, initial=1, coerce=int\
        ,widget = forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        gametype = [
            ('TCE', ((1, 'OBJ'), (2, 'BC'), (3, 'CTF'))),
            ('ET', ((4, 'CMP'), (5, 'OBJ'))),
        ]
        self.fields['game'].choices = gametype
    gametype_map = [0, 5, 7, 2, 4, 2]
    tce_last = 3

class ServerBrowser(GameBrowser):

    servers = GameServer.objects.all()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(-1, 'All')]
        for server in self.servers:
            choices.append((server.id, server.hostname_plain))
        self.fields['server'].choices = choices

    server = forms.TypedChoiceField(label='Server', required=False,\
        coerce=int, empty_value=-1\
        )
