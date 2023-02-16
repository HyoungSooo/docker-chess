# myapp/management/commands/mycommand.py
from django.core.management.base import BaseCommand
from api.models import ChessELO, ChessFenNextMoves, ChessMainline, ChessNotation, ChessNotationCheckPoint, ChessProcess, ChessPuzzles


class Command(BaseCommand):
    help = 'check the latest instance of MyModel'

    def handle(self, *args, **kwargs):
        ChessPuzzles.objects.all().delete()
        ChessFenNextMoves.objects.all().delete()
        ChessMainline.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Cleaning database'))
