#!/usr/bin/env python3
"""
API 服务启动脚本
"""
import os
import sys
import subprocess

def main():
    """启动 API 服务"""
    # 检查依赖
    print("🔍 检查依赖...")
    try:
        import fastapi
        import uvicorn
        print("✅ 依赖检查通过")
    except ImportError:
        print("❌ 缺少依赖，正在安装...")
        requirements = os.path.join(os.path.dirname(__file__), "requirements-api.txt")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements], check=True)
        print("✅ 依赖安装完成")
    
    # 设置环境变量
    os.environ.setdefault("PORT", "8000")
    os.environ.setdefault("HOST", "0.0.0.0")
    
    # 导入并运行应用
    print("🚀 启动公式识别 API 服务...")
    print(f"📡 监听地址: http://{os.getenv('HOST')}:{os.getenv('PORT')}")
    print(f"📄 API 文档: http://{os.getenv('HOST')}:{os.getenv('PORT')}/docs")
    print("=" * 50)
    
    # 启动 uvicorn
    from main import app
    import uvicorn
    
    uvicorn.run(
        app,
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT")),
        log_level="info",
        reload=True  # 开发模式启用热重载
    )

if __name__ == "__main__":
    main()