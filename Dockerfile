FROM ubuntu:18.04

RUN apt update && apt install -y \
  # lint / test
  shellcheck \
  python3-dev \
  gcc \
  python-tox \
  flake8 \
  # integration test
  sudo \
  ;

WORKDIR /workspace

ENV PYTHONPATH=/usr/lib/python3/dist-packages

# run tests and build .deb by default
CMD ["make", "all"]
