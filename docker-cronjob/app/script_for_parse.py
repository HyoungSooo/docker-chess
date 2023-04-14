import requests
import time
url = "http://host.docker.internal:8000"
start = time.time()
res = requests.get(f"{url}/chessapi/api/parse?num=0")
end = time.time()

if res.status_code == 200:
    print(f'done {end - start}')
else:
    print('parse fail')
