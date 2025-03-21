src = $(wildcard src/*.py)

.PHONY: run
run: | src/jobrad.egg-info
	.venv/bin/python -B -m jobrad

.PHONY: tidy
tidy:
	python3 -m isort ./src
	python3 -m black ./src

.venv/bin/python:
	python3 -m venv .venv

src/jobrad.egg-info: pyproject.toml $(src) | .venv/bin/python
	.venv/bin/python -m pip install -e '.[dev]'
