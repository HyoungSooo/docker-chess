import pandas as pd
import os
from typing import Union, List
import chess.pgn
import chess
import numpy as np
from api.models import ChessNotation, ChessNotationCheckPoint, ChessProcess, ChessFenNextMoves
from .utils import is_unique_avg
from django.db.models import QuerySet


class Processor:

    def __init__(self, fpath, num, checkpoint) -> None:
        self.df = pd.DataFrame()
        self.num = num
        self.msg = 'done'
        self.fpath = fpath
        self.checkpoint = checkpoint
        self.status = False
        self.next_checkpoint = checkpoint + num

        b, m = self.parse_data_to_csv()
        if b:
            self.msg = self.store_data()
        else:
            self.msg = m

    def parse_data_to_csv(self):
        pgn = open(self.fpath, 'r')

        for i in range(self.checkpoint):
            game = chess.pgn.read_game(pgn)

        game = chess.pgn.read_game(pgn)
        num = 0
        if game:
            while game != None:
                if num == self.num:
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

                num += 1
                game = chess.pgn.read_game(pgn)

            if game == None:
                self.status = True

            return True, 'done'
        else:
            return False, f'{self.fpath} is already done.'

    def store_data(self):

        success = 0
        error = 0

        for index, row in self.df.iterrows():
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

                notation = ChessNotation.objects.create(avg=elo, white=row["White"], black=row["Black"], site=row["Site"],
                                                        mainline=row["mainline"], opening=row["Opening"], event=row["Event"],
                                                        result=result)
                notation.save()

                success += 1
                error += 1
            except:
                pass
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

        self.parse()

    def parse(self):

        for i in self.data:
            board = chess.Board()
            moves = i.mainline.split(',')
            for cnt in range(len(moves) - 1):
                board.push_uci(moves[cnt])
                fen = board.fen()

                try:
                    data = ChessProcess.objects.get(fen=fen)
                except:
                    data = ChessProcess.objects.create(fen=fen)

                next_move = moves[cnt+1]

                try:
                    created_move = data.next_moves.get(next_move=next_move)

                except:
                    created_move = ChessFenNextMoves.objects.create(
                        fen=data, white=0, draw=0, black=0, next_move=next_move, cnt=0)

                created_move.cnt += 1
                if i.result == 'white':
                    created_move.white += 1
                elif i.result == 'black':
                    created_move.black += 1
                else:
                    created_move.draw += 1

                created_move.save()
