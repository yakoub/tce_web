from django.views.generic import DetailView, ListView, TemplateView
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Max, Q
from .models import *
from .mixins import *

class GameList(ServerBrowserMixin, StatisticsMixin, TeamsMixin, ListView):
    
    model = GameMatch
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.browse_dispatch(request)
        return super(GameList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(GameList, self).get_queryset()
        queryset = queryset.prefetch_related('gameplayer_set__player')\
            .prefetch_related('server').order_by('-id')
        return self.browse_query(queryset)

    def get_context_data(self, **kwargs):
        context = super(GameList, self).get_context_data(**kwargs)
        for game in context['object_list']:
            self.teams_context(game) 
        self.statistic_500_context(context)
        context['browse_form'] = self.browse_form
        self.pager_links(context)
        context['og_url'] = self.request.build_absolute_uri()

        return context

    def get_template_names(self):
        return ['game/list.html', 'list.html']


class GameView(StatisticsMixin, TeamsMixin, DetailView):

    model = GameMatch
    
    def get_queryset(self):
        queryset = super(GameView, self).get_queryset()
        return queryset.prefetch_related('gameplayer_set__player')\
            .prefetch_related('server')

    def get_context_data(self, **kwargs):
        context = super(GameView, self).get_context_data(**kwargs)
        context['og_url'] = self.request\
            .build_absolute_uri(self.object.get_absolute_url())
        self.teams_context(context['gamematch']) 
        self.statistic_500_context(context)
        return context

class PlayerView(ServerBrowserMixin, TeamsMixin, DetailView):

    model = PlayerIndex

    slug_field = 'id'

    def dispatch(self, request, *args, **kwargs):
        self.browse_dispatch(request)
        return super(PlayerView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PlayerView, self).get_context_data(**kwargs)
        game_list = GameMatch.objects\
            .filter(gameplayer__player = self.object.id)\
            .prefetch_related('gameplayer_set__player')\
            .prefetch_related('server')\
            .order_by('-id')
        game_list = self.browse_query(game_list).all()

        paginator = Paginator(game_list, 10)
        page_number = self.request.GET.get('page')
        context['game_list'] = paginator.get_page(page_number)
        for game in context['game_list']:
            self.teams_context(game) 
        context['browse_form'] = self.browse_form
        context['page_obj'] = context['game_list']
        self.pager_links(context)

        context['alias_list'] = PlayerIndex.objects\
            .filter(guid = self.object.guid)\
            .exclude(guid = '#')\
            .exclude(id = self.object.id).all()

        self.top_games(context)
        return context

    def top_games(self, context):
        queryset = GamePlayer.objects.filter(game__gametype=4)\
            .prefetch_related('game')\
            .order_by('-kills')
        if (self.object.guid != '#') :
            queryset = queryset.filter(player__guid=self.object.guid)
        else :
            queryset = queryset.filter(player=self.object.id)
        context['top_games'] = queryset[:5]

class GameServerView(BrowserMixin, TeamsMixin, DetailView):

    model = GameServer

    def dispatch(self, request, *args, **kwargs):
        self.browse_dispatch(request)
        return super(GameServerView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GameServerView, self).get_context_data(**kwargs)
        game_list = GameMatch.objects\
            .filter(gameplayer__game__server = self.object.id)\
            .prefetch_related('gameplayer_set__player')\
            .prefetch_related('server')\
            .order_by('-id')
        game_list = self.browse_query(game_list).all()

        paginator = Paginator(game_list, 10)
        page_number = self.request.GET.get('page')
        context['game_list'] = paginator.get_page(page_number)
        for game in context['game_list']:
            self.teams_context(game) 
        context['browse_form'] = self.browse_form
        context['page_obj'] = context['game_list']
        self.pager_links(context)
        context['og_url'] = self.request.build_absolute_uri()

        self.top_games(context)
        return context

    def top_games(self, context):
        queryset = GameMatch.objects.filter(server=self.object.id)\
            .annotate(player_count = Count('gameplayer'))\
            .order_by('-player_count')
        context['top_games'] = queryset[:5]


class Statistics(StatisticsMixin, TemplateView):

    template_name = "game/statistics_total.html"

    def dispatch(self, request, *args, **kwargs):
        GET = request.GET
        self.QtopGamesExtra = None
        self.QtopPlayersExtra = None
        if ('start' in GET):
            self.filter_form = StatisticsFilter(GET)
            form = self.filter_form
            if form.is_valid():
                Qgames = None
                Qplayers = None
                if (form.cleaned_data['start']):
                    start = form.cleaned_data['start'].replace(hour=0, minute=0, second=0)
                    Qgames = Q(created__gte=start)
                    Qplayers = Q(gameplayer__game__created__gte=start)
                if (form.cleaned_data['end']):
                    end = form.cleaned_data['end'].replace(hour=23, minute=59, second=59)
                    Qend = Q(created__lte=end)
                    Qgames = Qgames & Qend if Qgames else Qend
                    Qend = Q(gameplayer__game__created__lte=end)
                    Qplayers = Qplayers & Qend if Qplayers else Qend
                if (form.cleaned_data['exclude_bots']):
                    Qbots = Q(bot=False)
                    Qplayers = Qplayers & Qbots if Qplayers else Qbots
                if (form.cleaned_data['game'] == 1):
                    Qtype = Q(server__tcetest=True)
                    Qgames = Qgames & Qtype if Qgames else Qtype
                    Qgame = Q(gameplayer__game__server__tcetest=True)\
                    & Q(gameplayer__game__gametype=5)
                    Qplayers = Qplayers & Qgame if Qplayers else Qgame
                if (form.cleaned_data['game'] == 2):
                    Qtype = Q(server__tcetest=False)
                    Qgames = Qgames & Qtype if Qgames else Qtype
                    Qgame = Q(gameplayer__game__server__tcetest=False)\
                    & Q(gameplayer__game__gametype=4)
                    Qplayers = Qplayers & Qgame if Qplayers else Qgame

                self.QtopGamesExtra = Qgames
                self.QtopPlayersExtra = Qplayers

        else:
            self.QtopPlayersExtra = Q(bot=False)\
                & Q(gameplayer__game__server__tcetest=True)\
                & Q(gameplayer__game__gametype=5)
            self.QtopGamesExtra = Q(server__tcetest=True)

            self.filter_form = StatisticsFilter()
        return super(Statistics, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statistics_title'] = 'Total statistics'
        
        if self.QtopGamesExtra :
            self.QtopGames = self.QtopGames & self.QtopGamesExtra
        if self.QtopPlayersExtra :
            self.QtopPlayers = self.QtopPlayers & self.QtopPlayersExtra

        qs = self.top_games_qs.filter(self.QtopGames)
        context['top_games'] = self.top_games_annotate(qs)[:10]

        qs = self.top_players_qs.filter(self.QtopPlayers)
        context['top_players'] = self.top_players_annotate(qs).order_by('-total_score')[:10]

        context['filter_form'] = self.filter_form
        context['og_url'] = self.request.build_absolute_uri()

        return context
