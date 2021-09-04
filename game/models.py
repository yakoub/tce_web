from django.db import models
from django.urls import reverse

class GameMatch(models.Model):
    created = models.DateField('Created')
    mapname = models.CharField('Mapname', max_length=64)
    hostname = models.CharField('Hostname', max_length=64)
    team_red = models.SmallIntegerField('Terrorist')
    team_blue = models.SmallIntegerField('Specops')
    gametype = models.SmallIntegerField('Gametype')

    def __str__(self):
        return f"{self.id} {self.hostname=} {self.mapname=} {self.created=}"

    def get_absolute_url(self):
        return reverse('game:game-view', kwargs={'pk': self.pk})

    class Meta:
        db_table = 'game_match'
        managed = False

class GamePlayer(models.Model):
    game = models.ForeignKey(GameMatch, db_column='match_id',
        on_delete=models.DO_NOTHING)
    idx = models.SmallIntegerField('Idx', primary_key = True)
    team = models.SmallIntegerField('Team')
    name = models.CharField('Name', max_length=64)
    ping = models.SmallIntegerField('Ping')
    score = models.SmallIntegerField('Score')
    kills = models.SmallIntegerField('Kills')
    deaths = models.SmallIntegerField('Deaths')
    headshots = models.SmallIntegerField('Headshots')
    damage_given = models.SmallIntegerField('Damage given')
    damage_recieved = models.SmallIntegerField('Damage recieved')

    def __str__(self):
        return f"{self.name=} {self.idx=} {self.kills=} {self.score=}"

    class Meta:
        db_table = 'game_player'
        managed = False
