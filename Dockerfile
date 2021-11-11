FROM python:latest

SHELL [ "/bin/bash", "-c" ]

RUN apt-get update && \
    apt-get upgrade -y

RUN apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir -U 'pip'

WORKDIR /workspace

COPY requirements.txt /workspace

RUN pip3 install --no-cache-dir -r requirements.txt

ENV WORKON_HOME=~/.venvs

ENV PIPENV_VENV_IN_PROJECT=true
