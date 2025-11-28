#!/bin/bash

# 修复容器内的PATH和别名设置

CONTAINER_NAME="geektime_dl"

echo "修复容器内的geektime命令..."

# 1. 创建全局符号链接
docker exec $CONTAINER_NAME ln -sf /app/geektime /usr/local/bin/geektime

# 2. 更新PATH
docker exec $CONTAINER_NAME bash -c 'echo "export PATH=\"/app:\$PATH\"" >> ~/.bashrc'

# 3. 创建便捷别名
docker exec $CONTAINER_NAME bash -c 'echo "alias gt=\"/app/geektime\"" >> ~/.bashrc'
docker exec $CONTAINER_NAME bash -c 'echo "alias gq=\"/app/geektime query --config /app/config/geektime.cfg --auth-type token --no-login\"" >> ~/.bashrc'
docker exec $CONTAINER_NAME bash -c 'echo "alias ge=\"/app/geektime ebook --config /app/config/geektime.cfg --auth-type token --no-login\"" >> ~/.bashrc'

# 4. 重新加载bashrc
docker exec $CONTAINER_NAME bash -c 'source ~/.bashrc'

echo "✅ 修复完成！"
echo ""
echo "现在可以进入容器使用："
echo "  geektime query     # 查询课程"
echo "  gt query           # 使用别名查询"
echo "  gq                 # 使用快速别名查询"
echo "  ge 48              # 使用快速别名下载"