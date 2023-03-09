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
    white_elo = models.IntegerField()
    black_elo = models.IntegerField()
    site = models.TextField()
    mainline = models.TextField()
    opening = models.TextField()
    opening_fam = models.TextField()
    eco = models.CharField(max_length=10)
    event = models.TextField()
    result = models.TextField()


class ChessOpening(models.Model):
    fen = models.TextField()
    uci = models.TextField()
    name = models.TextField()


class ChessPuzzleThemes(models.Model):
    theme = models.TextField(unique=True)
    count = models.IntegerField()

    def __str__(self) -> str:
        return self.theme


class ChessPuzzle(models.Model):
    fen = models.TextField()
    moves = models.TextField()
    theme = models.ManyToManyField(ChessPuzzleThemes)
    url = models.URLField()
    opening_fam = models.TextField()
    opening_variation = models.TextField()
