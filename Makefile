version := $(shell python setup.py --version)
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
  $(HLT)make doc$(NC)         Builds man page and html documentation in doc/
  $(HLT)make build$(NC)       Builds a python package of auto_qc in dist/


endef
export HELP

help:
	clear && echo "$$HELP"

#################################################
#
# Build
#
#################################################

dist    := dist/$(name)-$(version).tar.gz

objs = \
       $(shell find auto_qc) \
       requirements/default.txt \
       setup.py \
       MANIFEST.in \
       man/auto-qc.1 \
       tox.ini

build: $(dist)

$(dist): $(objs)
	tox -e build

clean:
	rm -f dist/*

#################################################
#
# Documentation
#
#################################################

doc: man/auto-qc.1

man/%: man/%.mkd
	bundle exec ronn $<

#################################################
#
# Unit and Feature tests
#
#################################################

fmt:
	poetry run black auto_qc test bin features

autofeature:
	@clear && $(feature) || true
	@fswatch \
		--exclude 'pyc' \
		--one-per-batch	./auto_qc \
		--one-per-batch ./feature \
		| xargs -n 1 -I {} bash -c "$(feature)"

feature:
	@$(feature)

autotest:
	@clear && $(test) || true
	@fswatch \
		--exclude 'pyc' \
		--one-per-batch	./auto_qc \
		--one-per-batch ./test \
		| xargs -n 1 -I {} bash -c "$(test)"

test:
	@$(test)

# Commands for running tests and features
feature = tox -e feature $(FLAGS)
test    = clear && poetry run nosetests --rednose

#################################################
#
# Bootstrap project requirements for development
#
#################################################

bootstrap: Gemfile.lock .tox

.tox: requirements/default.txt requirements/development.txt
	tox --notest
	@touch $@

Gemfile.lock: Gemfile
	mkdir -p log
	bundle install --path vendor/ruby 2>&1 > log/gem.txt

.PHONY: bootstrap test feature autotest autofeature doc
