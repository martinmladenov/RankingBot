FROM python:3.8-alpine

ENV PYTHONUNBUFFERED=0
RUN apk add --no-cache build-base

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD commands commands
ADD handlers handlers
ADD helpers helpers
ADD services services
ADD tasks tasks
ADD utils utils
ADD constants.py constants.py
ADD main.py main.py

ENTRYPOINT [ "python", "./main.py" ]
