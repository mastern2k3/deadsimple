DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))


test:
	. $(DIR)/venv/bin/activate; \
	env PYTHONPATH=$(DIR)/src \
	pytest
