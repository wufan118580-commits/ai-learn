.PHONY: install install-dev format lint test clean all

help:
	@echo "可用命令:"
	@echo "  make install        安装依赖"
	@echo "  make test           运行所有测试"
	@echo "  make test-formula   运行公式识别测试"
	@echo "  make test-mathml    运行MathML转换测试"
	@echo "  make test-integration 运行集成测试"
	@echo "  make lint           代码检查"
	@echo "  make format         代码格式化"
	@echo "  make run            运行应用"
	@echo "  make clean          清理缓存"

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
	pytest tests/ -v --cov=src --cov-report=term-missing

test-formula:
	pytest tests/test_formula.py -v --tb=short

test-mathml:
	pytest tests/test_mathml_conversion.py -v --tb=short

test-integration:
	pytest tests/test_formula.py tests/test_mathml_conversion.py tests/test_document_processor.py -v

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
