FROM python:3.9-slim

WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建云函数启动文件
RUN echo '#!/bin/bash\npython app.py' > scf_bootstrap && chmod +x scf_bootstrap

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "app.py"]