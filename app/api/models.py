from django.db import models

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
    site = models.TextField()
    mainline = models.TextField()
    opening = models.TextField()
    event = models.TextField()
    result = models.TextField()


class ChessPuzzles(models.Model):
    pass


class NotationVersion(models.Model):
    vers = models.CharField(max_length=10, blank=True, null=True)


class ChessMainline(models.Model):
    checkpoint = models.IntegerField()


class ChessProcess(models.Model):
    fen = models.TextField(unique=True)


class ChessFenNextMoves(models.Model):
    fen = models.ForeignKey(
        ChessProcess, on_delete=models.PROTECT, related_name='next_moves')
    white = models.IntegerField(default=0)
    draw = models.IntegerField(default=0)
    black = models.IntegerField(default=0)
    next_move = models.CharField(max_length=10)
    cnt = models.IntegerField(default=0)
