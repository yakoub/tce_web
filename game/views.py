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

class StatisticsMixin:
    players_sql = """
        select pi.id, pi.name
        , sum(gp.kills) as total_kills, max(gp.kills) as max_kills
        from player_index pi
        inner join game_player gp on gp.player_id = pi.id
        inner join game_match gm on gm.id = gp.match_id
        where gm.id > %s and gm.gametype = 5 and pi.guid != '#'
        group by pi.guid
        order by total_kills desc
        limit 5
    """
    
    def statistic_context(self, context):
        last_id = GameMatch.objects.aggregate(id = Max('id'))
        since_id = last_id['id'] - 500

        context['top_games'] = GameMatch.objects\
            .filter(id__gt=since_id)\
            .annotate(player_count = Count('gameplayer'))\
                .order_by('-player_count')[:5]
        context['top_players'] = PlayerIndex.objects.raw(self.players_sql, [since_id])

class GameList(StatisticsMixin, TeamsMixin, ListView):
    
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


class GameView(StatisticsMixin, TeamsMixin, DetailView):

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

    top_sql_guid = """
        select gp.kills, gp.match_id, pi.id
        from player_index pi
        inner join game_player gp on pi.id = gp.player_id
        inner join game_match gm on gm.id = gp.match_id
        where pi.guid = %s and gm.gametype = 5
        order by gp.kills desc
        limit 5
    """

    top_sql_id = """
        select gp.kills, gp.match_id, pi.id
        from player_index pi
        inner join game_player gp on pi.id = gp.player_id
        inner join game_match gm on gm.id = gp.match_id
        where pi.id = %s and gm.gametype = 5
        order by gp.kills desc
        limit 5
    """

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

        if (self.object.guid != '#') :
            context['top_games'] = PlayerIndex.objects\
                .raw(self.top_sql_guid, [self.object.guid])
        else :
            context['top_games'] = PlayerIndex.objects\
                .raw(self.top_sql_id, [self.object.id])

        return context

