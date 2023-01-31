import requests
filename = 'v1.pgn'
url = "http://host.docker.internal:8000"

res = requests.get(f"{url}/chessapi/api/parse?filename={filename}&num=50")

if res.status_code == 200:
    data = requests.get(
        f"{url}/chessapi/api/getdata")
    print(data.json())
else:
    print('parse fail')
