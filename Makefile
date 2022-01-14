DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))


test:
	. $(DIR)/venv/bin/activate; \
	env PYTHONPATH=$(DIR)/src \
	pytest


lint:
	black --check $(DIR)/src
	pylint $(DIR)/src/*


benchmark:
	. $(DIR)/venv/bin/activate; \
	env PYTHONPATH=$(DIR)/src \
	python $(DIR)/src/tests/benchmarks.py resolver
	. $(DIR)/venv/bin/activate; \
	env PYTHONPATH=$(DIR)/src \
	python $(DIR)/src/tests/benchmarks.py hardcoded


publish:
	poetry publish --build


docs-serve:
	mkdocs serve
