from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, File, Schema
from ninja.files import UploadedFile
from ninja.security import django_auth
from django.http import JsonResponse, HttpResponse
from .models import (ChessELO, ChessNotation, ChessNotationCheckPoint,
                     ChessOpening, ChessPuzzle)
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

from stockfish import StockfishException

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
def parse_notation(request, num: int):
    v = int(ChessNotationCheckPoint.objects.last().fname.split('_')[0])
    filename = '_'.join(os.listdir('/app/data')[0].split('_')[1:])
    while True:
        try:
            checkpoint = ChessNotationCheckPoint.objects.get(
                fname=f'{v}_{filename}')
            if checkpoint.status == True:
                try:
                    os.remove(f'{settings.BASE_DIR}/data/{v}_{filename}')
                except:
                    pass
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


@api.get('/automate/eval')
def eval_pos(request, fen_list: str):
    stockfish = get_stockfish()
    fen_list = fen_list.replace('_', '/')
    board = chess.Board()
    res = []
    for i in fen_list.split(','):
        board.set_fen(i)
        try:
            stockfish = is_fen_valid(stockfish, board.fen())
            data = stockfish.get_evaluation()

            if data['type'] == 'mate':
                continue
            else:
                res.append((data['value'], stockfish.get_fen_position()))
        except:
            pass
    if len(res) == 0:
        return 'retry'

    return min(res, key=lambda n: n[0])[-1]


@api.get('/stockfish')
def stockfish_recommend(request, fen: str):
    stockfish = get_stockfish()
    stockfish = is_fen_valid(stockfish, fen)
    if stockfish:
        return stockfish.get_top_moves(3)

    return JsonResponse({'msg': 'fen is unvalid'})


@api.get('/automate')
def stockfish_recommend(request, fen: str, depth: int, level: int):
    stockfish = get_stockfish()
    stockfish.set_fen_position(fen)
    stockfish.set_skill_level(level)
    stockfish.set_depth(depth)
    if stockfish:
        try:
            return stockfish.get_best_move_time(1000)
        except StockfishException:
            return "Cannot make move"

    return JsonResponse({'msg': 'fen is unvalid'})


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


@api.get('/puzzle')
def get_random_puzzle(request):
    max_id = ChessPuzzle.objects.all().aggregate(max_id=Max("id"))['max_id']
    while True:
        pk = random.randint(1, max_id)
        puzzle = ChessPuzzle.objects.filter(
            pk=pk).values('fen', 'moves').first()
        if puzzle:
            return JsonResponse(puzzle, safe=False)


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


@api.get('/openingcountall')
def get_opening_count_all_top_10(request, rating: str = None):
    q = Q()
    if rating:
        for i in rating.split(','):
            q |= Q(avg__avg=i)

    data = list(ChessNotation.objects.filter(q).values_list('opening').annotate(
        dcount=Count('opening')).order_by('-dcount')[0:10])

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


@api.get('/countperrating')
def get_count_per_rating(request, rating: str = None):
    if not rating:
        data = list(ChessNotation.objects.all().values('avg__avg').annotate(
            cnt=Count('avg__avg')).order_by('avg__avg'))
        return JsonResponse(data, safe=False)

    else:
        q = Q()
        for i in rating.split(','):
            q |= Q(avg__avg=int(i))
        data = list(ChessNotation.objects.values('avg__avg').filter(
            q).annotate(cnt=Count('avg__avg')).order_by('avg__avg'))
        return JsonResponse(data, safe=False)


@api.get('/winrate')
def get_top_rate_opening(request, opening: str = None, rating: str = None):

    q = Q()

    if rating:
        for i in rating.split(','):
            q |= Q(avg=i)

    data = ChessNotation.objects.filter(
        opening=opening).first()._get_win_rate(q)

    return JsonResponse(data, safe=False)


@api.get('/solvedpuzzle')
def get_solved_puzzle_count(request):
    return ChessPuzzle.objects.filter(solved=True).count()


urlpatterns = [
    path('api/', api.urls)
]
