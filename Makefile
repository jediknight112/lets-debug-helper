MAJOR_VERSION = 1
MINOR_VERSION = 0
BUILD_NUMBER ?= 1

VERSION := $(MAJOR_VERSION).$(MINOR_VERSION).$(BUILD_NUMBER)

.PHONY: all
all: build test shell

.PHONY: clean
clean:
	@echo Cleaning environment ...
	# may not be a venv to remove, but just keep going in that case
	pipenv --rm || true
	rm -rf *.egg-info build dist .coverage Pipfile.lock
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '.pytest_cache' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +

.PHONY: check-env
check-env:
	@echo Checking environment ...
	pipenv --version

.PHONY: setup
setup:
	pipenv update --dev

.PHONY: lint
lint: setup
	pipenv run flake8 --verbose

.PHONY: build
build: check-env clean lint

.PHONY: test
test:
	pipenv run pytest --verbose --color=yes

.PHONY: coverage
coverage:
	pipenv run coverage run -m --include="letsdebughelper/*" --omit="/" pytest --verbose --color=yes
	pipenv run coverage report -m --include="letsdebughelper/*"

.PHONY: package
package: clean setup
	@echo Packaging application ...
	@echo Version: $(VERSION)
	mkdir -p build
	pipenv lock -r > build/requirements.txt
	VERSION=$(VERSION) \
		pipenv run python setup.py bdist_wheel

.PHONY: isolated
isolated:
	docker run \
		--rm \
		--tty \
		--volume $(shell pwd):/work:rw \
		--workdir /work \
	 	python:3.8 \
		/bin/bash -c "set -x && \
			pip install --upgrade pip && \
			pip install pipenv==2018.11.26 && \
			pipenv update --dev && \
			pipenv run flake8 --verbose && \
			pipenv run pytest --verbose --color=yes -p no:cacheprovider && \
			mkdir -p build && \
			pipenv lock -r > build/requirements.txt && \
			VERSION=$(VERSION) pipenv run python setup.py bdist_wheel"

.PHONY: shell
shell:
	PYTHONPATH=$(shell pwd) pipenv shell
