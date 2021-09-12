# Generated by Django 3.2.5 on 2021-09-02 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GameMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField(verbose_name='Created')),
                ('mapname', models.CharField(max_length=64, verbose_name='Mapname')),
                ('hostname', models.CharField(max_length=64, verbose_name='Hostname')),
                ('team_red', models.SmallIntegerField(verbose_name='Terrorist')),
                ('team_blue', models.SmallIntegerField(verbose_name='Specops')),
                ('gametype', models.SmallIntegerField(verbose_name='Gametype')),
            ],
            options={
                'db_table': 'game_match',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='GamePlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idx', models.SmallIntegerField(verbose_name='Idx')),
                ('team', models.SmallIntegerField(verbose_name='Team')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('ping', models.SmallIntegerField(verbose_name='Ping')),
                ('score', models.SmallIntegerField(verbose_name='Score')),
                ('kills', models.SmallIntegerField(verbose_name='Kills')),
                ('deaths', models.SmallIntegerField(verbose_name='Deaths')),
                ('headshots', models.SmallIntegerField(verbose_name='Headshots')),
            ],
            options={
                'db_table': 'game_player',
                'managed': False,
            },
        ),
    ]