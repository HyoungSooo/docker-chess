import requests
import time
url = "http://host.docker.internal:8000"
start = time.time()

try:

    res = requests.get(f"{url}/chessapi/api/mainline?num=200", timeout=50)

    end = time.time()

    if res.status_code == 200:
        print(f'done, time = {end-start}')
    else:
        print('parse fail')

except requests.exceptions.Timeout:
    print('timeout')
