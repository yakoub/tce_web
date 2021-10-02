from django.db.models import Q, Count, Max, Sum
from .models import *
from .forms import *

class BrowserMixin:

    Form = GameBrowser

    def query_filters(self):
        form = self.browse_form
        Qfilters = None
        if (form.cleaned_data['start']):
            start = form.cleaned_data['start'].replace(hour=0, minute=0, second=0)
            Qfilters = Q(created__gte=start)
        if (form.cleaned_data['end']):
            end = form.cleaned_data['end'].replace(hour=23, minute=59, second=59)
            Qend = Q(created__lte=end)
            Qfilters = Qfilters & Qend if Qfilters else Qend
        self.Qfilters = Qfilters
    
    def browse_dispatch(self, request):
        GET = request.GET
        self.Qfilters = None
        if ('start' in GET):
            self.browse_form = self.Form(GET)
            if self.browse_form.is_valid():
                self.query_filters()
        else:
            self.browse_form = self.Form()

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

class ServerBrowserMixin(BrowserMixin):

    Form = ServerBrowser

    def query_filters(self):
        super(ServerBrowserMixin, self).query_filters()
        form = self.browse_form
        Qfilters = self.Qfilters
        if (form.cleaned_data['server'] != -1):
            Qserver = Q(server=form.cleaned_data['server'])
            Qfilters = Qfilters & Qserver if Qfilters else Qserver
        self.Qfilters = Qfilters

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
    QtopPlayers = Q(gameplayer__game__gametype=4) & ~Q(guid='#')
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

