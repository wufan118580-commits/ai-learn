# 使用官方 Python 轻量级镜像
# https://hub.docker.com/_/python
FROM python:3-alpine

# 容器默认时区为UTC，如需使用上海时间请启用以下时区设置命令
# 设置时区，容器默认时区为UTC
RUN apk add tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo Asia/Shanghai > /etc/timezone

ENV APP_HOME /app
WORKDIR $APP_HOME

# 将本地代码拷贝到容器内
COPY . .

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 安装依赖
# 选用国内镜像源以提高下载速度
RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple && \
    pip config set global.trusted-host mirrors.cloud.tencent.com && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# 启动 Streamlit 应用
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]