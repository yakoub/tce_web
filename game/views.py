from django.views.generic import DetailView, ListView, TemplateView
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Max, Q
from .models import GameMatch, GamePlayer, PlayerIndex, GameServer
from .forms import GameBrowser, StatisticsFilter

class BrowserMixin:
    
    def browse_dispatch(self, request):
        GET = request.GET
        self.Qfilters = None
        if ('start' in GET):
            self.browse_form = GameBrowser(GET)
            form = self.browse_form
            if form.is_valid():
                Qfilters = None
                if (form.cleaned_data['start']):
                    start = form.cleaned_data['start'].replace(hour=0, minute=0, second=0)
                    Qfilters = Q(created__gte=start)
                if (form.cleaned_data['end']):
                    end = form.cleaned_data['end'].replace(hour=23, minute=59, second=59)
                    Qend = Q(created__lte=end)
                    Qfilters = Qfilters & Qend if Qfilters else Qend
                if (form.cleaned_data['server'] != -1):
                    Qserver = Q(server=form.cleaned_data['server'])
                    Qfilters = Qfilters & Qserver if Qfilters else Qserver
                self.Qfilters = Qfilters

        else:
            self.browse_form = GameBrowser()

    def browse_query(self, queryset):
        if (self.Qfilters):
            queryset = queryset.filter(self.Qfilters)
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
    QtopPlayers = Q(gameplayer__game__gametype=5) & ~Q(guid='#')
    def top_players_annotate(self, qs):
        return qs.annotate(total_kills = Sum('gameplayer__kills'))\
            .annotate(total_deaths = Sum('gameplayer__deaths'))\
            .annotate(total_score = Sum('gameplayer__score'))\
            .order_by('-total_kills')
    
    def statistic_500_context(self, context):
        last_id = GameMatch.objects.aggregate(id = Max('id'))
        since_id = (last_id['id'] - 500) if last_id['id'] else 0
        context['statistics_title'] = 'Last 500 games'

        qs = self.top_games_qs.filter(self.QtopGames & Q(id__gt=since_id))
        context['top_games'] = self.top_games_annotate(qs)[:5]

        qs = self.top_players_qs\
            .filter(self.QtopPlayers & Q(gameplayer__game__id__gt=since_id))
        context['top_players'] = self.top_players_annotate(qs)[:5]

class GameList(BrowserMixin, StatisticsMixin, TeamsMixin, ListView):
    
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

class PlayerView(BrowserMixin, TeamsMixin, DetailView):

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
        queryset = GamePlayer.objects.filter(game__gametype=5)\
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

                self.QtopGamesExtra = Qgames
                self.QtopPlayersExtra = Qplayers

        else:
            self.filter_form = StatisticsFilter()
        return super(Statistics, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statistics_title'] = 'Total statistics'
        
        if self.QtopGamesExtra :
            self.QtopGames = self.QtopGames & self.QtopGamesExtra
            self.QtopPlayers = self.QtopPlayers & self.QtopPlayersExtra

        qs = self.top_games_qs.filter(self.QtopGames)
        context['top_games'] = self.top_games_annotate(qs)[:10]

        qs = self.top_players_qs.filter(self.QtopPlayers)
        context['top_players'] = self.top_players_annotate(qs)[:10]

        context['filter_form'] = self.filter_form
        context['og_url'] = self.request.build_absolute_uri()

        return context
