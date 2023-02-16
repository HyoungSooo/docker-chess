# docker-chess-api

An API to interact with a database of chess PGN (Portable Game Notation) files.

### Features

- Using cronjob to convert a very large pgn file into data little by little periodically

The cycle can be modified by modifying the cronjob file and the script.py file in the docker-cronjob folder.

#### add file endpoint

post http://127.0.0.1:8000/chessapi/api/uploadfile

it will return uploaded file name

in docker-cronjob/app/script_for_parse.py

```
  import requests
  filename = "lichess_db_standard_rated_2015-04.pgn" # change here
  url = "http://host.docker.internal:8000"

  res = requests.get(f"{url}/chessapi/api/parse?filename={filename}&num=500")

  if res.status_code == 200:
      print('done')
  else:
      print('parse fail')

```

You can also change how often the script runs.
Same as regular cron cycle setting

in docker-cronjob/docker-compose.yml

```
  environment:
        - CRON_ENTRY=* * * * *(change here) python /app/script_for_parse.py
```

### endpoints

- `chessapi/api/uploadfile` upload pgn file in our server
- `chessapi/api/parse?filename=' '&num=' '` parse data from pgn file
- `chessapi/api/getdata` get all data
- `chessapi/api/mainline?num=<value>` Convert pgn data as much as the value to data
- `chessapi/api/movedata` get all movedata(which is parsed in /mainline)
- `chessapi/api/get_moveline?fen=' '` Get the next move of the given fen.
- `chessapi/api/eval_position?fen=' '` eval position using stockfish
- `chessapi/api/stockfish?fen=' '` get top moves (3) using stockfish

### how to use

```
<clone our repository>

cd <repository>

docker-compose build
docker-compose up
```

then go to http://127.0.0.1:8000/app/
also you can see endpoints here http://127.0.0.1:8000/chessapi/api/docs/
