import requests
import time
filename = "lichess_db_standard_rated_2015-04.pgn"
url = "http://host.docker.internal:8000"
start = time.time()
res = requests.get(f"{url}/chessapi/api/parse?filename={filename}&num=4000")
end = time.time()

if res.status_code == 200:
    print(f'done {end - start}')
else:
    print('parse fail')
