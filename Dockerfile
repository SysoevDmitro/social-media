FROM python:3.11.6-alpine3.18
LABEL maintaner="dimasysoev20000@gmail.com"

ENV PYTHONBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN adduser --disabled-password --no-create-home user

USER user
