FROM python:3.8-slim

RUN apt-get update && apt-get -y install sqlite3 fd-find entr
RUN pip3 install poetry

RUN mkdir -p /opt/rentamovie
COPY pyproject.toml poetry.lock /opt/rentamovie/
WORKDIR /opt/rentamovie
RUN poetry config virtualenvs.create false
RUN poetry install

ENV PYTHONPATH=src
ENV APP_SECRET=my-very-secret-dev-app-secret
EXPOSE 8000/tcp
CMD uvicorn --reload rentamovie:app --reload-dir src --log-level debug --host 0.0.0.0
