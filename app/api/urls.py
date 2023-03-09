from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, File, Schema
from ninja.files import UploadedFile
from ninja.security import django_auth
from django.http import JsonResponse, HttpResponse
from .models import (ChessELO, ChessNotation, ChessNotationCheckPoint,
                     ChessOpening, ChessPuzzle, ChessPuzzleThemes)
from django.db.models.functions import Length, Substr
from api.spark.processor import Processor
from django.core import serializers
from api.utils import write_pgn_chunk_files, get_stockfish, list_chunk, ask_to_chatgpt, is_fen_valid, split_opening_name
import chess.pgn
import os
import chess
from django.conf import settings
from multiprocessing import Pool
import random
from django.db.models import *


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


@api.get('/moveline')
def get_moveline(request, moves: str = None):
    board = chess.Board()
    if moves == None:
        data = list(ChessNotation.objects.annotate(submoves=Substr('mainline', 1, 4)).exclude(mainline='').values('submoves').annotate(cnt=Count('submoves'), white_win=Count(
            'result', filter=Q(result__iexact='white')), draw=Count('result', filter=Q(result__iexact='draw')), black_win=Count('result', filter=Q(result__iexact='black'))).order_by('-cnt'))

        return JsonResponse(data, safe=False)
    else:
        move = moves.split(',')
        data = list(ChessNotation.objects.filter(mainline__startswith=moves).exclude(mainline=moves).annotate(submoves=Substr(
            'mainline', 1+5*len(move), 4)).values('submoves').annotate(cnt=Count('submoves'), white_win=Count(
                'result', filter=Q(result__iexact='white')), draw=Count('result', filter=Q(result__iexact='draw')), black_win=Count('result', filter=Q(result__iexact='black'))).order_by('-cnt'))
        return JsonResponse(data, safe=False)


@api.get('/fen')
def get_fen_string_from_current_uci(request, moves: str):
    board = chess.Board()

    moves = moves.split(',')

    for i in moves:
        board.push_uci(i)

    return board.fen()


@api.get('/eval')
def eval_pos(request, fen: str):
    stockfish = get_stockfish()

    stockfish = is_fen_valid(stockfish, fen)
    if stockfish:
        return stockfish.get_evaluation()


@api.get('/stockfish')
def stockfish_recommend(request, fen: str):
    stockfish = get_stockfish()
    stockfish = is_fen_valid(stockfish, fen)
    if stockfish:
        return stockfish.get_top_moves(3)

    return JsonResponse({'msg': 'fen is unvalid'})


@api.get('/get_fen')
def get_fen(request, fen: str, next: str):
    stockfish = get_stockfish()

    stockfish = is_fen_valid(stockfish, fen)
    if stockfish:
        stockfish.make_moves_from_current_position([next])
        return stockfish.get_fen_position()
    else:
        return 'fen is unvalid'


@api.get('/battle_stockfish')
def stockfish_battle(request, level: int, depth: int, fen: str):
    stockfish = get_stockfish()
    stockfish.set_skill_level(level)
    stockfish.set_depth(depth)

    stockfish = is_fen_valid(stockfish, fen)
    if stockfish:

        return stockfish.get_best_move_time(1000)
    else:
        return 'unvalid fen'


@api.get('/opening')
def get_random_opening(request):
    num = random.randint(0, ChessOpening.objects.count())

    try:
        data = ChessOpening.objects.get(pk=num)
    except:
        first = ChessOpening.objects.first().pk
        data = ChessOpening.objects.get(pk=num + first)

    data_json = serializers.serialize('json', [data, ])

    return HttpResponse(data_json, content_type="text/json-comment-filtered")


@api.get('/opening_one')
def specific_opening_puzzle(request, name: str):
    try:
        data = ChessOpening.objects.filter(name=name).annotate(
            text_len=Length('uci')).values('name', 'fen', 'uci').order_by('text_len').last()
    except:
        return JsonResponse({'msg': 'error'})

    return JsonResponse(data)


@api.post('/ask')
def get_response_to_chatgpt(request, prommpt: str, end: bool):
    if not end:
        message = ask_to_chatgpt(prommpt)
        return JsonResponse({'msg': message})
    else:
        pass


@api.get('/puzzle')
def get_quzzle_query(request, theme: str):
    if theme != 'all':
        try:

            data = ChessPuzzleThemes.objects.get(theme=theme).chesspuzzle_set.values(
                'pk', 'fen__fen', 'moves').order_by("?").first()
            return JsonResponse(data)

        except:
            return JsonResponse({'msg': 'unvalid tag'})
    else:
        first = ChessPuzzle.objects.first().pk

        while True:
            num = random.randint(first, first + ChessPuzzle.objects.count())

            data = ChessPuzzle.objects.values(
                'pk', 'fen__fen', 'moves').filter(pk=num).first()
            if data:
                return data


@api.get('/puzzle_theme')
def get_puzzle_themes(request):
    data = list(ChessPuzzleThemes.objects.all().values('theme', 'count'))

    return JsonResponse(data, safe=False)


@api.get('/opening_puzzle')
def get_opening_puzzle(request, opening: str):
    name = split_opening_name(opening)

    data = ChessPuzzleThemes.objects.get(
        theme='opening').chesspuzzle_set.filter(opening_fam__icontains=name).order_by("?").values('opening_fam', 'opening_variation', 'moves', 'fen__fen').first()
    if data:

        return JsonResponse(data, safe=False)

    else:
        return JsonResponse({'msg': 'no puzzle'})


@api.get('/opening_family')
def get_opening_family(request):
    data = list(ChessOpening.objects.exclude(
        name__contains=':').annotate(sub=Substr('uci', 1, 4)).values('name', 'sub').all().distinct('name').order_by('name'))

    return JsonResponse(data, safe=False)


@api.get('/other_opening')
def get_other_related_opening(request, opening: str):
    data = list(ChessOpening.objects.filter(name__istartswith=opening).values(
        'name', 'fen', 'uci').distinct('name'))

    return JsonResponse(data, safe=False)


@api.get('/openingcount')
def get_opening_count_each_avg_top_5(request):

    data = ChessELO.objects.all().order_by('avg')
    res = {}
    for i in data:
        res[i.avg] = list(i.notation.values_list('opening').annotate(
            dcount=Count('opening')).order_by('-dcount')[0:5])

    return JsonResponse(res, safe=False)


@api.get('openingcountall')
def get_opening_count_all_top_5(request):

    data = list(ChessNotation.objects.values_list('opening').annotate(
        dcount=Count('opening')).order_by('-dcount')[0:5])

    return JsonResponse(data, safe=False)


@api.get('/notationcount')
def get_notation_count(request):
    return ChessNotation.objects.count()


@api.get('/currentfile')
def get_current_parse_file_name(request):
    return ChessNotationCheckPoint.objects.last().fname


@api.get('/pgnfilecount')
def get_count_parse_file(request):
    os.chdir('/app/data')

    return len(os.listdir())


urlpatterns = [
    path('api/', api.urls)
]
