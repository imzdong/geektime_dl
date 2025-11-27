#!/bin/bash

echo "=== 测试Docker构建 ==="

# 检查语法错误
echo "1. 检查Dockerfile语法..."
docker --version || echo "Docker未安装"

echo "2. 检查文件是否存在..."
ls -la Dockerfile setup.py geektime.py requirements/base.txt

echo "3. 检查Python依赖..."
if [ -f "requirements/base.txt" ]; then
    echo "requirements/base.txt内容:"
    cat requirements/base.txt
fi

echo "4. 尝试构建..."
docker build --no-cache -t test-geektime . 2>&1 | tee build.log

echo "=== 构建日志保存在 build.log ==="