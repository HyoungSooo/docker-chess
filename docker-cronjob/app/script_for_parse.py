import requests
filename = "lichess_db_standard_rated_2015-04.pgn"
url = "http://host.docker.internal:8000"

res = requests.get(f"{url}/chessapi/api/parse?filename={filename}&num=500")

if res.status_code == 200:
    print('done')
else:
    print('parse fail')
