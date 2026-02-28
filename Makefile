.PHONY: install format lint test

install:
	pip install --upgrade pip && \
	pip install -r requirements.txt

format:
	black *.py

lint:
	pylint --disable=R,C hello.py

test:
	python -m pytest -vv --cov=hello --cov-report=term-missing test_hello.py

all: install format lint test
