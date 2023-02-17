from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, File, Schema
from ninja.files import UploadedFile
from ninja.security import django_auth
from django.http import JsonResponse, HttpResponse
from .models import (ChessELO, ChessNotation, ChessNotationCheckPoint,
                     ChessMainline, ChessFenNextMoves, ChessProcess)
from api.spark.processor import Processor, MainlineProcessor
from django.core import serializers
from api.utils import write_pgn_chunk_files, get_stockfish, list_chunk
import chess.pgn
import os
import chess
from django.conf import settings
from multiprocessing import Pool


api = NinjaAPI()


@api.post('/uploadfile')
def uploadfile(request, uploaded_file: UploadedFile = File(...)):
  # UploadedFile is an alias to Django's UploadFile
    cnt = 0
    for chunk in uploaded_file.chunks(chunk_size=10**7):

        write_pgn_chunk_files(chunk, cnt, uploaded_file.name)
        cnt += 1

    return uploaded_file.name


@api.get('/parse')
def parse_notation(request, filename: str, num: int):
    v = 0
    while True:
        if not os.path.isfile(f'{settings.BASE_DIR}/data/{v}_{filename}'):
            for i in range(v):
                os.remove(f'{settings.BASE_DIR}/data/{i}_{filename}')
            return 'this file already done'
        try:
            checkpoint = ChessNotationCheckPoint.objects.get(
                fname=f'{v}_{filename}')
            if checkpoint.status == True:
                v += 1
                continue
            else:
                break
        except:
            checkpoint = ChessNotationCheckPoint.objects.create(
                fname=f'{v}_{filename}', checkpoint=0, status=False)
            break

    if checkpoint.checkpoint != 0:
        start = True
    else:
        start = False

    res = Processor(
        f'/app/data/{v}_{filename}', num, checkpoint.checkpoint, start)

    if res.status == True:
        checkpoint.status = True
    checkpoint.checkpoint = res.next_checkpoint

    checkpoint.save()

    return res.msg


@api.get('/getdata')
def get_data(request):
    data = ChessNotation.objects.all()
    data_json = serializers.serialize('json', data)
    return HttpResponse(data_json, content_type="text/json-comment-filtered")


@api.get('/mainline')
def parse_mainline(request, num: int):
    pool = Pool(3)
    first_pk = ChessNotation.objects.first()
    try:
        checkpoint = ChessMainline.objects.all()[0]
        if checkpoint.checkpoint < first_pk.pk:
            checkpoint.checkpoint = first_pk.pk
    except:
        checkpoint = ChessMainline.objects.create(checkpoint=first_pk.pk)
    data = ChessNotation.objects.filter(
        pk__gte=checkpoint.checkpoint, pk__lt=checkpoint.checkpoint + num)

    checkpoint.checkpoint += num

    checkpoint.save()
    if data:
        # MainlineProcessor(data)

        pool.map(MainlineProcessor, data)

    return


@api.get('/movedata')
def get_move_data(request):
    data = ChessFenNextMoves.objects.all()
    data_json = serializers.serialize('json', data)

    return HttpResponse(data_json, content_type="text/json-comment-filtered")


@api.get('/get_moveline')
def get_moveline(request, fen: str):
    stockfish = get_stockfish()

    if stockfish.is_fen_valid(fen):
        stockfish.set_fen_position(fen)
    try:
        fen_data = ChessProcess.objects.get(fen=stockfish.get_fen_position())

    except:
        return JsonResponse({"msg": "no data"})

    data = fen_data.next_moves.all().order_by('-cnt')
    data_json = serializers.serialize('json', data)

    return JsonResponse(data_json, safe=False)


@api.get('/eval_position')
def eval_pos(request, fen: str):
    stockfish = get_stockfish()

    if stockfish.is_fen_valid(fen):
        stockfish.set_fen_position(fen)
        return stockfish.get_evaluation()


@api.get('/stockfish')
def stockfish_recommend(request, fen: str):
    stockfish = get_stockfish()
    if stockfish.is_fen_valid(fen):
        stockfish.set_fen_position(fen)
        return stockfish.get_top_moves(3)

    return JsonResponse({'msg': 'fen is unvalid'})


@api.get('/get_fen')
def get_fen(request, fen: str, next: str):
    stockfish = get_stockfish()

    if stockfish.is_fen_valid(fen):
        stockfish.set_fen_position(fen)
        stockfish.make_moves_from_current_position([next])
        return stockfish.get_fen_position()
    else:
        return 'fen is unvalid'


@api.get('/battle_stockfish')
def stockfish_battle(request, level: int, depth: int, fen: str):
    stockfish = get_stockfish()
    stockfish.set_skill_level(level)
    stockfish.set_depth(depth)

    if stockfish.is_fen_valid(fen=fen):
        stockfish.set_fen_position(fen)

    return stockfish.get_best_move_time(1000)


urlpatterns = [
    path('api/', api.urls)
]
