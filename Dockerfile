FROM python:3.9-slim

# 设置标签信息
LABEL maintainer="geektime_dl" \
      description="极客时间电子书下载工具" \
      version="1.0"

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib-dev \
    libpng-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 创建应用用户
RUN useradd --create-home --shell /bin/bash geektime

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY requirements/ requirements/
COPY geektime_dl/ geektime_dl/
COPY setup.py .
COPY geektime.py .

# 安装Python依赖和应用
RUN pip install --no-cache-dir -r requirements/base.txt && \
    pip install -e . && \
    mkdir -p /app/data /app/cache && \
    chown -R geektime:geektime /app

# 切换到非root用户
USER geektime

# 创建默认配置目录
RUN mkdir -p /app/config

# 设置默认命令
CMD ["geektime", "--help"]