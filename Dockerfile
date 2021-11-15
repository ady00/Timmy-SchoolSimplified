# syntax=docker/dockerfile:1
FROM python:latest
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install sentry-sdk[flask]
RUN pip3 uninstall discord.py -y
COPY . .
CMD [ "python3", "main.py" ]