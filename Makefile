.PHONY: install install-dev format lint test clean all

help:
	@echo "可用命令:"
	@echo "  make install   安装依赖"
	@echo "  make test      运行测试"
	@echo "  make lint      代码检查"
	@echo "  make format    代码格式化"
	@echo "  make run       运行应用"
	@echo "  make clean     清理缓存"

install:
	pip install --upgrade pip && \
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

format:
	# black *.py
	black src/ tests/

lint:
	pylint --disable=R,C,W0718 src/ tests/
	# flake8 src/ tests/
	# mypy src/ --ignore-missing-imports

test:
	# python -m pytest -vv --cov=app --cov-report=term-missing test_app.py
	pytest tests/ -v --cov=src --cov-report=term-missing

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage

run:
	streamlit run src/app.py

# 本地开发常用命令组合
dev: install-dev format lint test

# CI/CD会用到的完整流程
all: install lint test
