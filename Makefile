name := auto_qc

HLT=\033[0;34m
NC=\033[0m

define HELP

Auto QC

The following commands are available for building and testing:

  $(HLT)make bootstrap$(NC)   Installs python dependencies locally
  $(HLT)make test$(NC)        Runs all unit tests defined in the test/ directory
  $(HLT)make feature$(NC)     Runs all feature tests defined in the features/ directory
  $(HLT)make fmt$(NC)         Formats code with ruff and prettier (markdown)
  $(HLT)make fmt_check$(NC)   Checks code formatting with ruff and prettier
  $(HLT)make build$(NC)       Builds a python package of auto_qc in dist/

endef
export HELP

help:
	clear && echo "$$HELP"

all: fmt_check test feature build

bootstrap:
	uv sync

fmt:
	uv run ruff check --fix auto_qc test features
	uv run ruff format auto_qc test features
	npx --yes prettier@2.2.1 --write .

fmt_check:
	uv run ruff check auto_qc test features
	uv run ruff format --check auto_qc test features
	npx --yes prettier@2.2.1 --check .

test:
	uv run pytest

feature:
	uv run behave --stop

build:
	uv build

clean:
	rm -f dist/*

.PHONY: help all bootstrap fmt fmt_check test feature build clean
