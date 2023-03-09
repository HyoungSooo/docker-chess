import pandas as pd
import os
from typing import Union, List
import chess.pgn
import chess
import numpy as np
from api.models import ChessNotation, ChessNotationCheckPoint
from .utils import is_unique_avg
from django.db.models import QuerySet


class Processor:

    def __init__(self, fpath, num, checkpoint, is_start=False) -> None:
        self.num = num
        self.msg = 'done'
        self.fpath = fpath
        self.checkpoint = checkpoint
        self.status = False
        self.next_checkpoint = checkpoint + num
        self.is_start = False

        self.parse_data_to_csv()

    def parse_data_to_csv(self):
        pgn = open(self.fpath, 'r')
        if self.is_start:
            for _ in range(1):
                game = chess.pgn.read_game(pgn)

        for i in range(self.checkpoint):
            game = chess.pgn.read_game(pgn)

        game = chess.pgn.read_game(pgn)
        num = 0
        if game:
            while game != None:
                if num == self.num:
                    break

                df = pd.DataFrame(
                    list(game.headers.values()) + [self.san_to_uci(game.mainline_moves())]).T
                df.columns = list(game.headers.keys()) + ['mainline']

                num += 1
                game = chess.pgn.read_game(pgn)
                n = self.store_data(df)

            if game == None:
                self.status = True
                if n != False:
                    n.delete()

        else:
            return

    def store_data(self, df):
        for index, row in df.iterrows():
            try:
                avg = (
                    (int(row['BlackElo']) + int(row['WhiteElo']) // 2) // 100) * 100
                elo = is_unique_avg(avg)

                if row['Result'] == '1-0':
                    result = 'white'
                elif row['Result'] == '0-1':
                    result = 'black'
                else:
                    result = 'draw'

                notation = ChessNotation.objects.create(avg=elo, white=row["White"], black=row["Black"], site=row["Site"], mainline=row["mainline"], opening=row["Opening"], event=row["Event"], white_elo=row['WhiteElo'], black_elo=row['BlackElo'], eco=row['ECO'],
                                                        result=result)
                notation.save()

                return notation
            except:
                return False

    def san_to_uci(self, mainline):
        uci = []
        for move in mainline:
            uci.append(move.uci())

        return ','.join(uci)
