from django.http import JsonResponse
import json
import chess
from api.models import *
import pandas as pd
from django.core import serializers


def rate(row, flag):
    total = row['white'] + row['draw'] + row['black']

    row['white_rate'], row['draw_rate'], row['black_rate'] = row['white'] / \
        total, row['draw'] / total, row['black'] / total

    if total <= flag:
        row['white_rate'], row['draw_rate'], row['black_rate'] = None, None, None

    return row


def run(svalue, fvalue, flag):

    dic = dict()

    for value in range(svalue, fvalue + 1, 100):

        avg = ChessELO.objects.get(avg=value)

        for i in avg.notation.all():
            if i.opening in dic:
                dic[i.opening][i.result] += 1
                dic[i.opening]['count'] += 1
            else:
                dic[i.opening] = {'white': 0,
                                  'draw': 0, 'black': 0, 'count': 0}
                dic[i.opening][i.result] += 1
                dic[i.opening]['count'] += 1

    res = {}
    df = pd.DataFrame(dic).T.sort_values('count', ascending=False)
    res['most_count'] = df[0:10].to_markdown()
    df = df.apply(lambda row: rate(row, flag=flag), axis=1)
    res['most_win_white'] = df.sort_values(
        'white_rate', ascending=False)[0:10].to_markdown()
    res['most_win_draw'] = df.sort_values(
        'draw_rate', ascending=False)[0:10].to_markdown()
    res['most_win_black'] = df.sort_values(
        'black_rate', ascending=False)[0:10].to_markdown()
    return res


def print_markdown(svalue, fvalue, flag):
    res = run(svalue, fvalue, flag)

    for key, value in res.items():
        print()
        print()
        print(key)
        print()
        print(value)
        print()
        print()


def opening_analyze(value):
    data = list(ChessNotation.objects.filter(
        opening__icontains=value).values_list('opening', 'result', 'mainline', 'avg__avg'))
    df = pd.DataFrame(list(data), columns=[
                      'opening', 'result', 'mainline', 'avg'])

    df.to_csv('./res.csv', sep='\t')

    return
