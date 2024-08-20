FROM python:3.12 AS requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.12
LABEL maintainer="Vitalii Vinnychenko <vinnichenko.vitaliy@gmail.com>"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

RUN apt-get update  \
    && apt-get -y install --no-install-recommends gcc mono-mcs libffi-dev build-essential postgresql  \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# set working directory
WORKDIR /usr/src/app

COPY --from=requirements-stage /tmp/requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
