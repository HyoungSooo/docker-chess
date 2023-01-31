from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, File, Schema
from ninja.files import UploadedFile
from ninja.security import django_auth
from django.http import JsonResponse, HttpResponse
from .models import ChessELO, ChessNotation, ChessNotationCheckPoint, ChessMainline
import pandas as pd
from api.spark.processor import Processor, MainlineProcessor
from django.core import serializers

api = NinjaAPI()


@api.post('/uploadfile')
def uploadfile(request, uploaded_file: UploadedFile = File(...)):
  # UploadedFile is an alias to Django's UploadFile
    with open(f'api\\dist\\notation\\{uploaded_file.name}', 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return uploaded_file.name


@api.get('/parse')
def parse_notation(request, filename: str, num: int):
    try:
        k = ChessNotationCheckPoint.objects.get(fname=filename[:-4])
        print(k.checkpoint, k.fname)
        msg = Processor(
            f'api\\dist\\notation\\{filename}', num, checkpoint=k.checkpoint, name=k.fname).msg
        print('done')
    except:
        print(filename[:-4])
        msg = Processor(
            f'api\\dist\\notation\\{filename}', num, checkpoint=None, name=filename[:-4]).msg

    return msg


@api.get('/getdata')
def get_data(request):
    data = ChessNotation.objects.all()
    data_json = serializers.serialize('json', data)
    return HttpResponse(data_json, content_type="text/json-comment-filtered")


@api.get('/mainline')
def parse_mainline(request, num: int):
    try:
        checkpoint = ChessMainline.objects.get(pk=1)
    except:
        checkpoint = ChessMainline.objects.create(checkpoint=0)

    data = ChessNotation.objects.filter(
        pk__gte=checkpoint.checkpoint, pk__lt=checkpoint.checkpoint + num)
    if data:
        MainlineProcessor(data)

    checkpoint.checkpoint += num

    checkpoint.save()

    return


urlpatterns = [
    path('api/', api.urls)
]
