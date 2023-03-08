from revChatGPT.V1 import Chatbot
from stockfish import Stockfish
import os
from django.conf import settings

import json


with open('/app/.config/config.json', 'r') as f:

    json_data = json.load(f)


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


def list_chunk(lst, n):
    return [lst[i:i+n] for i in range(0, len(lst), n)]


def ask_to_chatgpt(prompt):
    chatbot = Chatbot(config={
        "email": json_data['email'],
        "password": json_data["password"]
    })

    response = ""

    for data in chatbot.ask(
        prompt
    ):
        response = data["message"]

    return response


def is_fen_valid(stockfish, fen):
    if stockfish.is_fen_valid(fen):
        stockfish.set_fen_position(fen)

        return stockfish
    else:
        return False


def split_opening_name(value):
    name_split = value.split(':')
    opening_fam = name_split[0].strip(' ').replace(' ', '_')

    return opening_fam
