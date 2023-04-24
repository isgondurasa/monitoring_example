FROM python:3.11-alpine

RUN apk update \
  && apk add bash \
  && apk add --update --no-cache curl git libffi-dev libcurl pkgconfig\
  gcc g++ make libc-dev libxslt-dev python3-dev libev-dev \
  && rm -rf /var/cache/apk/*


RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}://root/.local/bin://root/.poetry/bin"

COPY poetry.lock pyproject.toml /app/
WORKDIR /app

RUN pip install --upgrade pip && poetry config virtualenvs.create false \
  && poetry lock --no-update && poetry install --no-interaction --no-ansi

COPY . /app
