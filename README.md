# docker-chess-api

An API to interact with a database of chess PGN (Portable Game Notation) files.

### Features

- Using cronjob to convert a very large pgn file into data little by little periodically

The cycle can be modified by modifying the cronjob file and the script.py file in the docker-cronjob folder.

```
  TZ=Asia/Seoul
* * * * * python /app/script.py >> /var/log/cron.log 2>&1
#
```

### endpoints

- `chessapi/api/uploadfile` upload pgn file in our server
- `chessapi/api/parse?filename=' '&num=' '` to data
- `chessapi/api/getdata` get all data

### future works

This is the initial step to create a chess database. We will complete this project by making the database more sophisticated and applying various endpoint chess puzzle algorithms.

### how to use

```
<clone our repository>

cd <repository>

docker-compose build
docker-compose up
```
