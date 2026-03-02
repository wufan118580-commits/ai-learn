.PHONY: install install-dev format lint test clean all

install:
	pip install --upgrade pip && \
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

format:
	black *.py

lint:
	pylint --disable=R,C app.py

test:
	python -m pytest -vv --cov=app --cov-report=term-missing test_app.py

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage

# 本地开发常用命令组合
dev: install-dev format lint test

# CI/CD会用到的完整流程
all: install lint test
