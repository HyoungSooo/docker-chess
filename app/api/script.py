from api.models import ChessPuzzle
from django.db import connection
from django.core.management.color import no_style
import pandas as pd
from api.models import ChessOpening, ChessPuzzle
import chess
from api.utils import get_stockfish
from multiprocessing import Pool
import time


def opening_run():

    data = pd.read_csv('/app/chess_opening.csv', delimiter='\t')

    for idx, row in data.iterrows():
        board = chess.Board()
        moves = row['uci'].split(' ')
        for i in moves:
            board.push_uci(i)
        ChessOpening.objects.create(
            fen=board.fen(), uci=','.join(moves), name=row['name'])


class PuzzleProcess:
    def __int__(self):
        self.puzzle = None
        self.data = None

    def puzzle_run(self):
        pool = Pool(2)
        chunk_size = 10**4
        col = "PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningFamily,OpeningVariation"
        fpath = "/app/lichess_db_puzzle.csv"
        point = ChessPuzzle.objects.count() // 10000

        for cnt, chunk in enumerate(pd.read_csv(fpath, chunksize=chunk_size, delimiter=',', header=None, names=col.split(','))):
            print(chunk.head())
            if cnt < point:
                continue

            for idx, row in chunk.iterrows():

                self.puzzle = ChessPuzzle.objects.create(fen=row['FEN'], moves=row['Moves'], url=row['GameUrl'],
                                                         opening_fam=row['OpeningFamily'], opening_variation=row['OpeningVariation'], theme=row['Themes'])
