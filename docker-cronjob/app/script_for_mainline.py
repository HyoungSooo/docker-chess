import requests
import time
url = "http://host.docker.internal:8000"
start = time.time()

res = requests.get(f"{url}/chessapi/api/mainline?num=100")

end = time.time()

if res.status_code == 200:
    print(f'done, time = {end-start}')
else:
    print('parse fail')
