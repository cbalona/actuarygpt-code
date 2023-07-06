.PHONY: venv setup

SHELL := /bin/bash

PYTHON_INTERPRETER := python
VENV := source .venv/bin/activate

PROJECT_CONFIG := requirements.in

venv: .venv/touchfile

.venv/touchfile: requirements.txt
	$(VENV); pip-sync
	touch .venv/touchfile

requirements.txt: $(PROJECT_CONFIG)
	$(VENV); pip-compile --output-file=requirements.txt --resolver=backtracking $(PROJECT_CONFIG)

setup:
	virtualenv .venv
	$(VENV); pip install --upgrade pip setuptools wheel
	$(VENV); pip install pip-tools