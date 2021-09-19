from django.views.generic import DetailView, ListView
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Max
from .models import GameMatch, GamePlayer, PlayerIndex
from datetime import datetime, timedelta

class TeamsMixin:

    def teams_context(self, game):
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
        game.player_count = len(game.red_players) + len(game.blue_players)

class StatisicsMixin:
    
    def statistic_context(self, context):
        start = datetime.now() - timedelta(days=2)
        context['top_games'] = GameMatch.objects\
            .filter(created__gt=start)\
            .annotate(player_count = Count('gameplayer'))\
                .order_by('-player_count')[:5]
        context['top_players'] = PlayerIndex.objects\
            .filter(gameplayer__game__created__gt=start,\
                gameplayer__game__gametype=5)\
            .annotate(total_kills = Sum('gameplayer__kills'))\
            .annotate(max_kills = Max('gameplayer__kills'))\
            .order_by('-total_kills')[:5]

class GameList(StatisicsMixin, TeamsMixin, ListView):
    
    model = GameMatch
    paginate_by = 5

    def get_queryset(self):
        queryset = super(GameList, self).get_queryset()
        return queryset.prefetch_related('gameplayer_set__player').order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(GameList, self).get_context_data(**kwargs)
        for game in context['object_list']:
            self.teams_context(game) 
        self.statistic_context(context)
        return context

    def get_template_names(self):
        return ['game/list.html', 'list.html']


class GameView(StatisicsMixin, TeamsMixin, DetailView):

    model = GameMatch
    
    def get_queryset(self):
        queryset = super(GameView, self).get_queryset()
        return queryset.prefetch_related('gameplayer_set__player')

    def get_context_data(self, **kwargs):
        context = super(GameView, self).get_context_data(**kwargs)
        self.teams_context(context['gamematch']) 
        self.statistic_context(context)
        return context

class PlayerView(TeamsMixin, DetailView):

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
        for game in context['game_list']:
            self.teams_context(game) 

        context['alias_list'] = PlayerIndex.objects\
            .filter(guid = self.object.guid)\
            .exclude(guid = '#')\
            .exclude(id = self.object.id).all()
        return context

