from django.views.generic import DetailView, ListView, TemplateView
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Max, Q
from datetime import datetime, timedelta
from .models import GameMatch, GamePlayer, PlayerIndex
from .forms import GameBrowser

class BrowserMixin:

    def browse_form(self, context):
        if ('start' in self.request.GET):
            context['browse_form'] = GameBrowser(self.request.GET)
        else:
            context['browse_form'] = GameBrowser()

    def browse_query(self, queryset):
        if ('start' in self.request.GET):
            start = self.request.GET['start'] + ' 00:00:00'
            end = self.request.GET['end'] + ' 23:59:59'
            queryset = queryset.filter(created__gte=start, created__lte=end)
        return queryset

    def pager_links(self, context):
        get_params = self.request.GET.copy()
        page_obj = context['page_obj']
        if (page_obj.has_previous()):
            get_params['page'] = context['page_obj'].previous_page_number()
            context['previous_page_params'] = get_params.urlencode()
        if (page_obj.has_next()):
            get_params['page'] = context['page_obj'].next_page_number()
            context['next_page_params'] = get_params.urlencode()


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

    top_games_qs = GameMatch.objects
    QtopGames = Q(gameplayer__team__lt=3)
    def top_games_annotate(self, qs):
        return qs.annotate(player_count = Count('gameplayer'))\
            .order_by('-player_count')

    top_players_qs = PlayerIndex.objects
    QtopPlayers = Q(gameplayer__game__gametype=5)
    def top_players_annotate(self, qs):
        return qs.annotate(total_kills = Sum('gameplayer__kills'))\
            .annotate(max_kills = Max('gameplayer__kills'))\
            .order_by('-total_kills')
    
    def statistic_500_context(self, context):
        last_id = GameMatch.objects.aggregate(id = Max('id'))
        since_id = last_id['id'] - 500
        context['statistics_title'] = 'Last 500 games'

        qs = self.top_games_qs.filter(self.QtopGames & Q(id__gt=since_id))
        context['top_games'] = self.top_games_annotate(qs)[:5]

        qs = self.top_players_qs\
            .filter(self.QtopPlayers & Q(gameplayer__game__id__gt=since_id))
        context['top_players'] = self.top_players_annotate(qs)[:5]

class GameList(BrowserMixin, StatisticsMixin, TeamsMixin, ListView):
    
    model = GameMatch
    paginate_by = 10

    def get_queryset(self):
        queryset = super(GameList, self).get_queryset()
        queryset = queryset.prefetch_related('gameplayer_set__player').order_by('-id')
        return self.browse_query(queryset)

    def get_context_data(self, **kwargs):
        context = super(GameList, self).get_context_data(**kwargs)
        for game in context['object_list']:
            self.teams_context(game) 
        self.statistic_500_context(context)
        self.browse_form(context)
        self.pager_links(context)
        context['og_url'] = self.request.build_absolute_uri()

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
        context['og_url'] = self.request\
            .build_absolute_uri(self.object.get_absolute_url())
        self.teams_context(context['gamematch']) 
        self.statistic_500_context(context)
        return context

class PlayerView(BrowserMixin, TeamsMixin, DetailView):

    model = PlayerIndex

    slug_field = 'id'

    def get_context_data(self, **kwargs):
        context = super(PlayerView, self).get_context_data(**kwargs)
        game_list = GameMatch.objects\
            .filter(gameplayer__player_id = self.object.id)\
            .prefetch_related('gameplayer_set__player')\
            .order_by('-id')
        game_list = self.browse_query(game_list).all()

        paginator = Paginator(game_list, 10)
        page_number = self.request.GET.get('page')
        context['game_list'] = paginator.get_page(page_number)
        for game in context['game_list']:
            self.teams_context(game) 
        self.browse_form(context)
        context['page_obj'] = context['game_list']
        self.pager_links(context)

        context['alias_list'] = PlayerIndex.objects\
            .filter(guid = self.object.guid)\
            .exclude(guid = '#')\
            .exclude(id = self.object.id).all()

        self.top_games(context)
        return context

    def top_games(self, context):
        queryset = GamePlayer.objects.filter(game__gametype=5)\
            .order_by('-kills')
        if (self.object.guid != '#') :
            queryset = queryset.filter(player__guid=self.object.guid)
        else :
            queryset = queryset.filter(player=self.object.id)
        context['top_games'] = queryset[:5]

class Statistics(StatisticsMixin, TemplateView):

    template_name = "game/statistics_total.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statistics_title'] = 'Total statistics'

        qs = self.top_games_qs.filter(self.QtopGames)
        context['top_games'] = self.top_games_annotate(qs)[:10]

        qs = self.top_players_qs.filter(self.QtopPlayers)
        context['top_players'] = self.top_players_annotate(qs)[:10]

        return context
