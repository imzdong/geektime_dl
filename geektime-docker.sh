#!/bin/bash

# geektime-docker.sh - Docker版本的geektime_dl便捷启动脚本

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装，请先安装Docker${NC}"
    exit 1
fi

# 创建必要的目录
mkdir -p "$SCRIPT_DIR/output" "$SCRIPT_DIR/config" "$SCRIPT_DIR/cache"

# 检查配置文件
CONFIG_FILE="$SCRIPT_DIR/config/geektime.cfg"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}警告: 配置文件不存在，正在创建模板...${NC}"
    if [ -f "$SCRIPT_DIR/geektime.cfg.example" ]; then
        cp "$SCRIPT_DIR/geektime.cfg.example" "$CONFIG_FILE"
        echo -e "${GREEN}配置文件模板已创建: $CONFIG_FILE${NC}"
        echo -e "${YELLOW}请编辑配置文件并填入你的认证信息${NC}"
    else
        echo -e "${RED}错误: 无法找到配置文件模板${NC}"
        exit 1
    fi
fi

# 显示使用帮助
if [ $# -eq 0 ]; then
    echo -e "${GREEN}geektime_dl Docker版本${NC}"
    echo ""
    echo "用法: $0 [命令] [参数]"
    echo ""
    echo "示例:"
    echo "  $0 query                    # 查询所有课程"
    echo "  $0 ebook 48                 # 下载课程48"
    echo "  $0 ebook 48 --comments-count 50  # 下载课程48并设置评论数量"
    echo ""
    echo "目录映射:"
    echo "  output/  -> /app/output   (下载文件)"
    echo "  config/  -> /app/config   (配置文件)"
    echo "  cache/   -> /app/cache    (缓存文件)"
    exit 0
fi

# 构建镜像（如果不存在）
if ! docker images | grep -q "geektime_dl"; then
    echo -e "${YELLOW}构建Docker镜像...${NC}"
    cd "$SCRIPT_DIR"
    docker build -t geektime_dl .
    if [ $? -ne 0 ]; then
        echo -e "${RED}Docker镜像构建失败${NC}"
        exit 1
    fi
fi

# 运行Docker容器
echo -e "${GREEN}执行命令: geektime $@${NC}"
docker run --rm \
    -v "$SCRIPT_DIR/output:/app/output" \
    -v "$SCRIPT_DIR/config:/app/config" \
    -v "$SCRIPT_DIR/cache:/app/cache" \
    -e PYTHONUNBUFFERED=1 \
    geektime_dl "$@"