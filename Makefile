WHL_VERSION ?= patch
DOCKER_IMG ?= lets-debug:test
artifacts = ./artifacts
pkg_name = lets-debug-helper
docker_workdir = /workspace

# this is kinda goofy...  ensure relevant things run in a docker.
docker_run := docker run -t --rm -v $$PWD:$(docker_workdir) $(DOCKER_IMG)
IS_DOCKER = $(shell test -f /.dockerenv && echo '1' || echo '0')
ifeq ($(IS_DOCKER),1)
	runner := bash -c
else
	runner := $(docker_run) bash -c
endif

.PHONY: all
all: build test shell

.PHONY: build
build: check-env clean lint

.PHONY: clean
clean:
	@echo Cleaning environment ...
	# may not be a venv to remove, but just keep going in that case
	rm -rf *.egg-info build dist .coverage
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '.pytest_cache' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +

.PHONY: check-env
check-env:
	@echo Checking environment ...
	poetry version

.PHONY: setup
setup:
	poetry install
	poetry update

.PHONY: lint
lint: setup
	poetry run flake8 --verbose

.PHONY: test
test:
	poetry run pytest --verbose --color=yes

.PHONY: coverage
coverage:
	poetry run pytest --cov-report term-missing:skip-covered --cov=letsdebughelper --verbose --color=yes

.PHONY: bump_py_version
bump_py_version:
	poetry version $(WHL_VERSION)

.PHONY: package
package: clean bump_py_version
	@echo Packaging application ...
	poetry build

.PHONY: docker_all
all: docker_build docker_check_env docker_lint docker_test

.PHONY: docker_build
docker_build:  ## build docker image
ifeq ($(IS_DOCKER),0)
	docker build -t $(DOCKER_IMG) .
endif

.PHONY: docker_check_env
docker_check_env:
	@echo Checking environment ...
	docker run --rm -v $(PWD):/workspace $(DOCKER_IMG) poetry --version

.PHONY: docker_setup
docker_setup:
	docker run --rm -v $(PWD):/workspace $(DOCKER_IMG) poetry update

.PHONY: docker_lint
docker_lint: docker_setup
	docker run --rm -v $(PWD):/workspace $(DOCKER_IMG) poetry run flake8 --verbose

.PHONY: docker_test
docker_test:
	docker run --rm -v $(PWD):/workspace $(DOCKER_IMG) poetry run pytest --verbose --color=yes letsdebughelper

.PHONY: docker_coverage
docker_coverage:
	docker run --rm -v $(PWD):/workspace $(DOCKER_IMG) poetry run pytest --cov-report term-missing:skip-covered --cov=letsdebughelper --verbose --color=yes

.PHONY: docker_package
docker_package: docker_clean docker_setup
	@echo Packaging application ...
	docker run --rm -v $(PWD):/workspace $(DOCKER_IMG) poetry build

.PHONY: docker_clean
docker_clean:
	@echo Cleaning environment ...
	# may not be a venv to remove, but just keep going in that case
	rm -rf *.egg-info build dist .coverage
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '.pytest_cache' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
