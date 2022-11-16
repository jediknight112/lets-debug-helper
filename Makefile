WHL_VERSION ?= patch

help: ## display this help
	@awk -F ':|##' \
		'/^[^\t].+?:.*?##/ {printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF}' \
		$(MAKEFILE_LIST)

.PHONY: all
all: build test shell

.PHONY: check_env
check_env:
	@echo Checking environment ...
	poetry check

.PHONY: setup
setup:
	poetry install

.PHONY: format
format:
	poetry run yapf --style pyproject.toml --in-place --recursive letsdebughelper/*

.PHONY: lint
lint: setup
	poetry run flake8 --verbose letsdebughelper

.PHONY: test
test:
	poetry run pytest --verbose --color=yes letsdebughelper

.PHONY: coverage
coverage:
	poetry run pytest \
	--cov-report lcov:coverage/lcov.info \
	--cov-report term-missing:skip-covered \
	--cov=letsdebughelper --verbose \
	--color=yes letsdebughelper

.PHONY: bump_py_version
bump_py_version:
	poetry version $(WHL_VERSION)

.PHONY: package
package: bump_py_version
	@echo Packaging application ...
	poetry build

.PHONY: publish
publish:
	@echo Publishing application ...
	poetry publish

.PHONY: clean
clean:
	@echo Cleaning environment ...
	# may not be a venv to remove, but just keep going in that case
	rm -rf *.egg-info build dist .coverage coverage
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '.pytest_cache' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +
