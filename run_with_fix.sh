#!/bin/bash

# 公式识别功能运行脚本 - 禁用OpenCV GUI
# 用于在无GUI环境中运行应用

# 设置环境变量禁用OpenCV的Qt GUI
export QT_QPA_PLATFORM=offscreen
export OPENCV_IO_ENABLE_OPENEXR=1
export MESA_GL_VERSION_OVERRIDE=3.3

echo "🚀 启动公式识别功能（已禁用OpenCV GUI）"
echo "📝 环境变量已设置:"
echo "   QT_QPA_PLATFORM=$QT_QPA_PLATFORM"
echo "   OPENCV_IO_ENABLE_OPENEXR=$OPENCV_IO_ENABLE_OPENEXR"
echo ""

# 运行应用
streamlit run src/app.py --server.headless true
