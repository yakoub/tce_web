from django.views.generic import DetailView, ListView
from django.core.paginator import Paginator
from .models import GameMatch, GamePlayer, PlayerIndex

class GameList(ListView):
    
    model = GameMatch
    paginate_by = 5

    def get_queryset(self):
        queryset = super(GameList, self).get_queryset()
        return queryset.prefetch_related('gameplayer_set__player').order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(GameList, self).get_context_data(**kwargs)
        for game in context['object_list']:
            game.red_players = []
            game.blue_players = []
            game.spectators = []
            for player in game.gameplayer_set.all():
                if (player.team == 1):
                    game.red_players.append(player)
                elif (player.team ==2):
                    game.blue_players.append(player)
                else :
                    game.spectators.append(player)
        return context

    def get_template_names(self):
        return ['game/list.html', 'list.html']


class GameView(DetailView):

    model = GameMatch
    
    def get_queryset(self):
        queryset = super(GameView, self).get_queryset()
        return queryset.prefetch_related('gameplayer_set__player')

    def get_context_data(self, **kwargs):
        context = super(GameView, self).get_context_data(**kwargs)
        game = context['gamematch']
        game.red_players = []
        game.blue_players = []
        game.spectators = []
        for player in game.gameplayer_set.all():
            if (player.team == 1):
                game.red_players.append(player)
            elif (player.team ==2):
                game.blue_players.append(player)
            else :
                game.spectators.append(player)

        return context

class PlayerView(DetailView):

    model = PlayerIndex

    def get_context_data(self, **kwargs):
        context = super(PlayerView, self).get_context_data(**kwargs)
        game_list = GameMatch.objects\
            .filter(gameplayer__player_id = self.object.id)\
            .prefetch_related('gameplayer_set__player')\
            .order_by('-id').all()

        paginator = Paginator(game_list, 10)
        page_number = self.request.GET.get('page')
        context['game_list'] = paginator.get_page(page_number)

        context['alias_list'] = PlayerIndex.objects\
            .filter(guid = self.object.guid)\
            .exclude(guid = '#')\
            .exclude(id = self.object.id).all()
        return context

