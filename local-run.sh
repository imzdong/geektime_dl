#!/bin/bash

# local-run.sh - 本地Python运行脚本（替代Docker方案）

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Geektime_dl 本地运行脚本 ===${NC}"

# 检查Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}错误: Python未安装${NC}"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo -e "${YELLOW}使用Python: $PYTHON_CMD${NC}"

# 安装依赖
if [ -f "requirements/base.txt" ]; then
    echo -e "${YELLOW}安装Python依赖...${NC}"
    $PYTHON_CMD -m pip install -r requirements/base.txt
fi

# 创建数据目录
echo -e "${YELLOW}创建数据目录...${NC}"
mkdir -p data config cache

# 复制配置文件
if [ ! -f "config/geektime.cfg" ]; then
    if [ -f "geektime.cfg.example" ]; then
        cp geektime.cfg.example config/geektime.cfg
        echo -e "${GREEN}✅ 配置文件已创建: config/geektime.cfg${NC}"
        echo -e "${YELLOW}⚠️  请编辑配置文件并填入你的认证信息${NC}"
    else
        echo -e "${RED}错误: 找不到配置文件模板${NC}"
        exit 1
    fi
fi

# 设置环境变量
export GEEKTIME_OUTPUT_DIR="./data"
export GEEKTIME_CONFIG_DIR="./config" 
export GEEKTIME_CACHE_DIR="./cache"

# 运行命令
if [ $# -eq 0 ]; then
    echo -e "${GREEN}=== 显示帮助信息 ===${NC}"
    $PYTHON_CMD geektime.py --help
else
    echo -e "${GREEN}=== 执行命令: geektime.py $@ ===${NC}"
    $PYTHON_CMD geektime.py "$@"
fi

echo ""
echo -e "${BLUE}=== 数据目录 ===${NC}"
echo -e "${YELLOW}下载文件: ./data${NC}"
echo -e "${YELLOW}配置文件: ./config/geektime.cfg${NC}"
echo -e "${YELLOW}缓存文件: ./cache${NC}"