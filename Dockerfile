# 使用官方 Python 轻量级镜像
# https://hub.docker.com/_/python
FROM python:3.11-slim

# 设置时区，容器默认时区为UTC
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV APP_HOME /app
WORKDIR $APP_HOME

# 安装系统依赖（使用国内镜像源）
RUN echo "deb http://mirrors.cloud.tencent.com/debian/ trixie main" > /etc/apt/sources.list && \
    echo "deb http://mirrors.cloud.tencent.com/debian-security/ trixie-security main" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 将本地代码拷贝到容器内
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
# 禁用OpenCV的GUI功能（在无GUI环境中）
ENV QT_QPA_PLATFORM=offscreen
ENV OPENCV_IO_ENABLE_OPENEXR=1

# 安装依赖
# 选用国内镜像源以提高下载速度
RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple && \
    pip config set global.trusted-host mirrors.cloud.tencent.com && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# 启动 Streamlit 应用
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]