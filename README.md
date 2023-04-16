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

### app features

chess analysis mode
- It operates the same as the analysis function provided by lichess and chess.com for the data collected through cronjob. Using stockfish version 11, it also provides an ai analysis function, and if you enter fen, the entered fen position is displayed.

play against the chess engine
- Ability to play against chess engines. Difficulty can be adjusted as you can directly set the stockfish skill level and depth.

chess puzzle
- Provides chess puzzle rush function by utilizing chess puzzle data provided by lichess database. Unlike existing lichess and chess.com, it provides a function to check your number in advance.

chess opening puzzle and database
- Provides a chess opening database. It provides a search function using simple JavaScript and a function to learn chess openings in a puzzle format.

chess automate(developing)
- A chess automate mode is under development. At the end of the game, you will be given a choice. The options are to add the computer and your pieces, or to increase the computer's intelligence even further.


### how to use

```
<clone this repository>

cd <repository>

docker-compose build
docker-compose up
```

then go to http://127.0.0.1:8000/app/
also you can see endpoints here http://127.0.0.1:8000/chessapi/api/docs/
