FROM pollett/python-cron:3

WORKDIR /app

COPY ./requirements.txt /app

COPY script.py /app

RUN python -m pip install requests
