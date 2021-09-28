from django.db import models
from django.urls import reverse

class GameServer(models.Model):
    hostname = models.CharField('Hostname', max_length=64)
    hostname_plain = models.CharField('Hostname plain', max_length=64)
    ip = models.CharField('IP', max_length=64)
    port = models.IntegerField('Port')

    def get_absolute_url(self):
        return reverse('game:server-view', kwargs={'pk': self.pk})

    class Meta:
        db_table = 'game_server'
        managed = False

class GameMatch(models.Model):
    created = models.DateTimeField('Created')
    mapname = models.CharField('Mapname', max_length=64)
    server = models.ForeignKey(GameServer, db_column='server_id',
        on_delete=models.DO_NOTHING)
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

class PlayerIndex(models.Model):
    guid = models.CharField('guid', max_length=32, primary_key = True)
    id = models.IntegerField('id', unique=True)
    name = models.CharField('Name', max_length=64)
    name_plain = models.CharField('Name plain', max_length=64)

    def get_absolute_url(self):
        return reverse('game:player-view', kwargs={'slug': self.id})

    class Meta:
        db_table = 'player_index'
        managed = False

class GamePlayer(models.Model):
    game = models.ForeignKey(GameMatch, db_column='match_id',
        on_delete=models.DO_NOTHING)
    idx = models.SmallIntegerField('Idx', primary_key = True)
    team = models.SmallIntegerField('Team')
    player = models.ForeignKey(PlayerIndex, db_column='player_id',
        to_field='id',
        on_delete=models.DO_NOTHING)
    ping = models.SmallIntegerField('Ping')
    score = models.SmallIntegerField('Score')
    kills = models.SmallIntegerField('Kills')
    deaths = models.SmallIntegerField('Deaths')
    headshots = models.SmallIntegerField('Headshots')
    damage_given = models.SmallIntegerField('Damage given')
    damage_recieved = models.SmallIntegerField('Damage recieved')

    def __str__(self):
        return f"{self.player_id=} {self.idx=} {self.kills=} {self.score=}"

    class Meta:
        db_table = 'game_player'
        managed = False
