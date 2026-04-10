# 文档学习助手项目 Makefile

.PHONY: help test test-all test-formula test-mathml test-integration lint format clean deps

help: ## 显示帮助信息
	@echo "文档学习助手项目构建工具"
	@echo ""
	@echo "用法: make [target]"
	@echo ""
	@echo "本地开发 (无需 Docker):"
	@echo "  make deps        安装依赖"
	@echo "  make dev         完整开发环境设置"
	@echo "  make run-ui      启动 Streamlit UI"
	@echo "  make test        运行测试"
	@echo ""
	@echo "Docker 相关:"
	@echo "  make build       构建所有镜像 (api + ui)"
	@echo "  make deploy      docker-compose 一键部署"
	@echo "  make status      查看容器状态"
	@echo "  make logs        查看容器日志"
	@echo "  make stop        停止所有服务"
	@echo ""
	@echo "CI/CD:"
	@echo "  make lint        代码风格检查 (同 Actions)"
	@echo "  make format      格式化代码"
	@echo "  make clean       清理临时文件"
	@echo ""

test: ## 运行所有测试
	pytest tests/ -v

test-formula: ## 运行公式识别相关测试
	pytest tests/test_formula.py tests/test_mathml_conversion.py -v

test-mathml: ## 运行MathML转换测试
	pytest tests/test_mathml_conversion.py -v

test-document: ## 运行文档处理测试
	pytest tests/test_document_processor.py -v

test-mermaid: ## 运行Mermaid图表测试
	pytest tests/test_mermaid.py -v

test-integration: ## 运行集成测试
	pytest tests/ --cov=src --cov-report=term-missing

lint: ## 代码风格检查
	flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 tests/ --count --select=E9,F63,F7,F82 --show-source --statistics

format: ## 格式化代码
	black src/ tests/
	isort src/ tests/

clean: ## 清理临时文件
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/

deps: ## 安装开发依赖
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

dev: deps clean ## 开发环境设置

build-api: ## 构建API镜像
	docker build -f Dockerfile.api -t workspace-api:latest .

build-ui: ## 构建UI镜像
	docker build -f Dockerfile.ui -t workspace-ui:latest .

build: build-api build-ui ## 构建所有镜像

run-api: ## 运行API服务
	cd api && python run.py

run-ui: ## 运行UI服务
	streamlit run src/app.py

deploy: ## 部署应用
	./deploy.sh

deploy-api: ## 部署API服务
	docker-compose up -d api

deploy-ui: ## 部署UI服务
	docker-compose up -d ui

logs: ## 查看容器日志
	docker-compose logs -f

stop: ## 停止所有服务
	docker-compose down

restart: ## 重启所有服务
	docker-compose restart

status: ## 查看容器状态
	docker-compose ps

health: ## 检查服务健康状态
	curl -s http://localhost:8000/health || echo "API服务未运行"
	curl -s http://localhost:8501 || echo "UI服务未运行"

backup: ## 备份数据
	docker run --rm -v document-learning-assistant_html_data:/data -v $(pwd):/backup alpine tar czf /backup/html_data_backup_$(date +%Y%m%d).tar.gz /data

docker-clean: ## 清理Docker资源
	docker system prune -a -f

setup: deps clean ## 完整项目设置
	@echo "项目设置完成"
	@echo ""
	@echo "日常开发流程:"
	@echo "  make run-ui      # 启动 UI 服务 (开发模式)"
	@echo "  make test        # 跑测试 (push develop 前先跑)"
	@echo ""
	@echo "发版流程:"
	@echo "  1. git push origin develop          → Actions: 测试+构建验证"
	@echo "  2. gh pr create --base main         → Actions: PR 门禁"
	@echo "  3. 合并 PR                          → Actions: 自动部署"

ci: lint test build ## 本地模拟完整 CI 流程（测试 + 检查 + 构建镜像）
	@echo ""
	@echo "✅ CI 流程全部通过，可以安全 push"