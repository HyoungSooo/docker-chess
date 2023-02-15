from stockfish import Stockfish
import os
from django.conf import settings


def write_pgn_chunk_files(value, version, name):
    with open(f"{settings.BASE_DIR}/data/{version}_{name}", 'wb+') as f:
        f.write(value)
    f.close()


def get_stockfish():
    os.chdir("/app/api/stockfish_10_linux/Linux")
    file_dir = os.getcwd()

    stockfish = Stockfish(
        path=file_dir + '/stockfish_10_x64')

    return stockfish
