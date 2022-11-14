FROM python:3.8-alpine

RUN apk add --no-cache build-base

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ARG BOTDIR=/bot

ADD . ${BOTDIR}

ARG GNAME=rankingbot
ARG UNAME=rankingbot
RUN addgroup -S ${GNAME} && adduser -S -G ${GNAME} -h ${BOTDIR} ${UNAME}
USER ${UNAME}

WORKDIR ${BOTDIR}

ENTRYPOINT [ "python", "-u", "/bot/main.py" ]
