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
from api.utils import write_pgn_chunk_files, get_stockfish
import chess.pgn
import os
import chess
from django.conf import settings

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
    first_pk = ChessNotation.objects.first()
    try:
        checkpoint = ChessMainline.objects.all()[0]
        if checkpoint.checkpoint < first_pk.pk:
            checkpoint.checkpoint = first_pk.pk
        print(checkpoint)
    except:
        checkpoint = ChessMainline.objects.create(checkpoint=first_pk.pk)
        print(checkpoint)
    data = ChessNotation.objects.filter(
        pk__gte=checkpoint.checkpoint, pk__lt=checkpoint.checkpoint + num)
    print(len(data))
    if data:
        MainlineProcessor(data)

    checkpoint.checkpoint += num

    checkpoint.save()

    return


@api.get('/movedata')
def get_move_data(request):
    data = ChessFenNextMoves.objects.all()
    data_json = serializers.serialize('json', data)

    return HttpResponse(data_json, content_type="text/json-comment-filtered")


@api.get('/get_moveline')
def get_moveline(request, uci: str):

    uci = uci.split(',')
    board = chess.Board()
    for i in uci:
        board.push_uci(i)

    try:
        fen_data = ChessProcess.objects.get(fen=board.fen())

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


urlpatterns = [
    path('api/', api.urls)
]
