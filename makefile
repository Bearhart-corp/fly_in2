# ######

# Vars
PYTHON = python3
PIP    = $(PYTHON) -m pip install -r
FLAKE8 = $(PYTHON) -m flake8
MYPY   = $(PYTHON) -m mypy

# install dependancies

install:
	$(PIP) requirements.txt
	$(PIP) requirements_dev.txt

run:
	$(PYTHON) -m src.fly_in "src/config.txt"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -exec rm -f {} +
	rm -rf .mypy_cache

build:
	python -m build
	rm -drf src/mazegen.egg-info

debug:
	$(PYTHON) -m pdb src/fly_in.py "src/config.txt"

lint:
	$(FLAKE8) . --exclude=lib,.venv,.mypy_cache
	$(MYPY) src \
	--warn-return-any --warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs


.PHONY: install run clean build debug lint
