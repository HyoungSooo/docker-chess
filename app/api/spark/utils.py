from api.models import ChessELO

def is_unique_avg(value):
    try:
        data = ChessELO.objects.create(avg = value)
        data.save()
        return data
    except:
        return ChessELO.objects.get(avg = value)