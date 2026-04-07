#!/bin/bash

# 文档学习助手 Docker 部署脚本

set -e

echo "===================================="
echo "  文档学习助手 Docker 部署脚本"
echo "===================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：未找到 Docker，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误：未找到 docker-compose，请先安装 Docker Compose"
    exit 1
fi

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，从 .env.example 创建..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ 已创建 .env 文件"
        echo "⚠️  请编辑 .env 文件，配置 DEEPSEEK_API_KEY"
        echo ""
        read -p "是否现在配置 API Key？(y/n): " configure_api
        if [ "$configure_api" = "y" ]; then
            read -p "请输入 DeepSeek API Key: " api_key
            sed -i "s/your_deepseek_api_key_here/$api_key/" .env
            echo "✅ API Key 已配置"
        fi
    else
        echo "❌ 错误：未找到 .env.example 文件"
        exit 1
    fi
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p config
echo "✅ 目录创建完成"
echo ""

# 验证 .env 文件配置
echo "🔍 验证配置..."
if [ ! -f .env ]; then
    echo "❌ 错误：.env 文件不存在"
    exit 1
fi

if grep -q "your_deepseek_api_key_here" .env; then
    echo "⚠️  警告：.env 中的 API Key 还是默认值，请手动配置"
    echo "   编辑 .env 文件，设置 DEEPSEEK_API_KEY"
fi
echo "✅ 配置验证完成"
echo ""

# 停止并删除旧容器
echo "🛑 停止旧容器..."
docker-compose down
echo "✅ 旧容器已停止"
echo ""

# 构建新镜像（分离部署）
echo "🔨 构建 Docker 镜像..."
echo "📦 镜像构建计划："
echo "  1. API 镜像 (包含 PyTorch + CUDA, ~8GB)"
echo "  2. UI 镜像 (轻量级, ~300MB)"
echo ""
echo "⚠️  注意：首次构建需要下载 PyTorch 基础镜像"
echo ""

# 构建 API 镜像
echo "🔨 构建 API 镜像..."
docker build -f Dockerfile.api -t workspace-api:latest .
echo "✅ API 镜像构建完成"

# 构建 UI 镜像
echo "🔨 构建 UI 镜像..."
docker build -f Dockerfile.ui -t workspace-ui:latest .
echo "✅ UI 镜像构建完成"

echo ""

# 启动容器
echo "🚀 启动容器..."
docker-compose up -d
echo "✅ 容器已启动"
echo ""

# 显示容器状态
echo "📊 容器状态："
docker-compose ps
echo ""

# 显示日志
echo "📋 查看应用日志（Ctrl+C 退出）："
echo "===================================="
docker-compose logs -f
