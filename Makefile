version = 3.0.0
name    := auto_qc

HLT=\033[0;34m
NC=\033[0m

define HELP

Auto QC Version $(version)

The following commands are available for building and testing:

  $(HLT)make bootstrap$(NC)   Installs python and ruby dependencies locally
  $(HLT)make test$(NC)        Runs all unit tests defined in the test/
  $(HLT)make feature$(NC)     Runs all feature tests defined in the features/
  $(HLT)make fmt$(NC)         Runs black cod formatting
  $(HLT)make build$(NC)       Builds a python package of auto_qc in dist/


endef
export HELP

help:
	clear && echo "$$HELP"

all: test feature build

#################################################
#
# Build
#
#################################################

dist    := dist/$(name)-$(version).tar.gz

objs = $(shell find auto_qc -type f ! -name "*.pyc") pyproject.toml

build: $(dist)

$(dist): $(objs)
	poetry build

clean:
	rm -f dist/*


#################################################
#
# Unit and Feature tests
#
#################################################


fmt:
	poetry run isort auto_qc tests features bin
	poetry run black auto_qc test bin features

fmt_check:
	poetry run isort --check --diff auto_qc tests features
	poetry run black --check auto_qc test bin features

autofeature:
	@clear && $(feature) || true
	@fswatch \
		--exclude 'pyc' \
		--one-per-batch	./auto_qc \
		--one-per-batch ./feature \
		| xargs -n 1 -I {} bash -c "$(feature)"

feature:
	@$(feature)

autotest: fmt
	@clear && $(test) || true
	@fswatch \
		--exclude 'pyc' \
		--one-per-batch	./auto_qc \
		--one-per-batch ./test \
		| xargs -n 1 -I {} bash -c "$(test)"

test: fmt
	@$(test)

# Commands for running tests and features
feature = poetry run behave --stop --no-skipped
test    = clear && poetry run nosetests --rednose

#################################################
#
# Bootstrap project requirements for development
#
#################################################

bootstrap:
	poetry install

Gemfile.lock: Gemfile
	mkdir -p log
	bundle install --path vendor/ruby 2>&1 > log/gem.txt

.PHONY: bootstrap test feature autotest autofeature doc
