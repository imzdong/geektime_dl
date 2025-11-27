#!/bin/bash

# deploy.sh - 快速部署脚本

set -e

IMAGE_NAME=${1:-geektime_dl}
VERSION=${2:-latest}

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Geektime_dl 部署脚本 ===${NC}"

# 检查镜像是否存在
if ! docker images | grep -q "$IMAGE_NAME.*$VERSION"; then
    echo -e "${RED}错误: 镜像 $IMAGE_NAME:$VERSION 不存在${NC}"
    echo -e "${YELLOW}请先运行: ./build.sh${NC}"
    exit 1
fi

# 创建必要的目录
echo -e "${YELLOW}创建数据目录...${NC}"
mkdir -p data config cache

# 复制配置文件模板
if [ ! -f "config/geektime.cfg" ] && [ -f "geektime.cfg.example" ]; then
    cp geektime.cfg.example config/geektime.cfg
    echo -e "${GREEN}配置文件已创建: config/geektime.cfg${NC}"
    echo -e "${YELLOW}请编辑配置文件填入认证信息${NC}"
fi

# 停止旧容器
echo -e "${YELLOW}停止旧容器...${NC}"
docker-compose down 2>/dev/null || true

# 启动新容器
echo -e "${YELLOW}启动新容器...${NC}"
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 部署成功${NC}"
else
    echo -e "${RED}❌ 部署失败${NC}"
    exit 1
fi

# 显示状态
echo ""
echo -e "${BLUE}=== 容器状态 ===${NC}"
docker ps | grep geektime_dl

echo ""
echo -e "${BLUE}=== 使用方法 ===${NC}"
echo -e "${YELLOW}查看帮助:${NC}"
echo "  docker exec geektime_dl geektime --help"
echo ""
echo -e "${YELLOW}查询课程:${NC}"
echo "  docker exec geektime_dl geektime query"
echo ""
echo -e "${YELLOW}下载课程:${NC}"
echo "  docker exec geektime_dl geektime ebook 48 --comments-count 50"
echo ""
echo -e "${YELLOW}查看下载结果:${NC}"
echo "  ls -la data/"
echo ""
echo -e "${YELLOW}查看日志:${NC}"
echo "  docker-compose logs -f geektime"