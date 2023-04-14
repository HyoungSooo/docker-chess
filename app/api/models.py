from django.db import models
from django.db.models import *
from django.core import serializers
import json
# Create your models here.


class ChessELO(models.Model):
    avg = models.IntegerField(unique=True, blank=False)


class ChessNotationCheckPoint(models.Model):
    fname = models.TextField(unique=True)
    checkpoint = models.IntegerField()
    status = models.BooleanField(default=False)


class ChessNotation(models.Model):
    avg = models.ForeignKey(
        ChessELO, on_delete=models.CASCADE, related_name='notation')
    white = models.TextField()
    black = models.TextField()
    white_elo = models.IntegerField()
    black_elo = models.IntegerField()
    site = models.TextField()
    mainline = models.TextField()
    opening = models.TextField()
    opening_fam = models.TextField()
    eco = models.CharField(max_length=10)
    event = models.TextField()
    result = models.TextField()

    def _get_win_rate(self, q=None):
        if not q:
            q = Q()
        data = list(ChessNotation.objects.filter(opening=self.opening).filter(q).values('opening').annotate(cnt=Count('opening'), white_win=Count(
            'result', filter=Q(result__iexact='white')), draw=Count('result', filter=Q(result__iexact='draw')), black_win=Count('result', filter=Q(result__iexact='black'))))
        data = data[0]
        return {'opening': self.opening, 'white_win': round((data['white_win'] / data['cnt'])*100, 2), 'black_win': round((data['black_win'] / data['cnt'])*100, 2), 'draw': round((data['draw'] / data['cnt'])*100, 2)}


class ChessOpening(models.Model):
    fen = models.TextField()
    uci = models.TextField()
    name = models.TextField()


class ChessPuzzle(models.Model):
    fen = models.TextField()
    moves = models.TextField()
    theme = models.TextField(default='')
    url = models.URLField()
    opening_fam = models.TextField()
    opening_variation = models.TextField()
    solved = models.BooleanField(default=False)
    one_time_solved = models.BooleanField(default=True)

    def check_solved_at_once(self):
        self.one_time_solved = False

    def check_its_solved(self):
        self.solved = True

    def get_themes(self):
        return self.theme.split(' ')

    def reset_sovled_data(*args, **kwargs):
        ChessPuzzle.objects.all().update(solved=False, one_time_solved=True)
