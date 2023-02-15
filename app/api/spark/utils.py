from api.models import ChessELO


def is_unique_avg(value):
    try:
        return ChessELO.objects.get(avg=value)

    except:
        data = ChessELO.objects.create(avg=value)
        data.save()
        return data


def write_pgn_chunk_files(value, version, name):
    with open(f"api\\dist\\notation\\{version}_{name}", 'wb+') as f:
        f.write(value)
    f.close()
