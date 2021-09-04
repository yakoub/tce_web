from django.views.generic import DetailView, ListView
from .models import GameMatch, GamePlayer

class GameList(ListView):
    
    model = GameMatch
    paginate_by = 5

    def get_queryset(self):
        queryset = super(GameList, self).get_queryset()
        return queryset.prefetch_related('gameplayer_set').order_by('-id')

    def get_template_names(self):
        return ['game/list.html', 'list.html']


class GameView(DetailView):

    model = GameMatch
    
    def get_queryset(self):
        queryset = super(GameView, self).get_queryset()
        return queryset.prefetch_related('gameplayer_set')

    def get_context_data(self, **kwargs):
        context = super(GameView, self).get_context_data(**kwargs)
        context['players'] = self.object.gameplayer_set.all()
        return context

class PlayerView(DetailView):

    model = GamePlayer
