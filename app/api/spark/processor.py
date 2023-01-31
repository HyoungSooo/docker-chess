import pandas as pd
from typing import Union, List
import chess.pgn
import chess
import numpy as np
from api.models import NotationVersion, ChessELO, ChessNotation, ChessNotationCheckPoint
from .utils import is_unique_avg
from django.db.models import QuerySet


class Processor:

    def __init__(self, fpath, num, checkpoint=None, name=None) -> None:
        self.df = pd.DataFrame()
        self.num = num
        self.checkpoint = checkpoint
        self.name = name
        self.msg = 'done'

        b, m = self.parse_data_to_csv(fpath)
        if b:
            self.msg = self.store_data()
        else:
            self.msg = m

    def parse_data_to_csv(self, fpath):

        value = open(fpath, 'r')
        if self.checkpoint:
            for i in range(self.checkpoint):
                game = chess.pgn.read_game(value)

        game = chess.pgn.read_game(value)
        cnt = 0
        if game:
            while game != None:
                if cnt >= self.num:
                    break

                if not self.df.empty:
                    df = pd.DataFrame(
                        list(game.headers.values()) + [self.san_to_uci(game.mainline_moves())]).T
                    df.columns = list(game.headers.keys()) + ['mainline']
                    self.df = pd.concat([self.df, df], ignore_index=True)
                else:
                    self.df = pd.DataFrame(
                        list(game.headers.values()) + [self.san_to_uci(game.mainline_moves())]).T
                    self.df.columns = list(game.headers.keys()) + ['mainline']

                game = chess.pgn.read_game(value)
                cnt += 1

            try:
                data = ChessNotationCheckPoint.objects.get(
                    fname=self.name)
                data.checkpoint += cnt
                data.save()
                print('done', data.checkpoint)
            except:
                print('fail')
                o = ChessNotationCheckPoint.objects.create(
                    fname=self.name, checkpoint=cnt)
                o.save()
            return True, 'done'
        else:
            return False, f'{self.name} is already done.'

    def store_data(self):

        success = 0
        error = 0

        for index, row in self.df.iterrows():
            avg = (
                (int(row['BlackElo']) + int(row['WhiteElo']) // 2) // 100) * 100
            elo = is_unique_avg(avg)

            notation = ChessNotation.objects.create(avg=elo, white=row["White"], black=row["Black"], site=row["Site"],
                                                    mainline=row["mainline"], opening=row["Opening"], event=row["Event"],
                                                    result=row["Result"])
            notation.save()

            success += 1
            error += 1
        self.msg = f'success : {success}, fail : {error}'
        return

    def san_to_uci(self, mainline):
        uci = []
        for move in mainline:
            uci.append(move.uci())

        return ','.join(uci)


class MainlineProcessor:
    def __init__(self, data: List[ChessNotation]) -> None:
        self.data = data
        self.df = pd.DataFrame()
        self.current = None

    def parse(self):

        for i in self.data:
            board = chess.Board()
            for j in i.mainline:
                board.push_uci(j)
                fen = board.fen()

                pass
