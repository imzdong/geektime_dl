#!/bin/bash

# build.sh - 构建和发布Docker镜像脚本

set -e

IMAGE_NAME="geektime_dl"
VERSION=${1:-latest}

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Geektime_dl Docker 构建脚本 ===${NC}"
echo -e "${YELLOW}镜像名称: $IMAGE_NAME${NC}"
echo -e "${YELLOW}版本标签: $VERSION${NC}"
echo ""

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    exit 1
fi

# 清理旧镜像（可选）
echo -e "${YELLOW}清理旧镜像...${NC}"
docker rmi $IMAGE_NAME:$VERSION 2>/dev/null || true
docker rmi $IMAGE_NAME:latest 2>/dev/null || true

# 尝试构建镜像（按优先级尝试不同版本）
echo -e "${YELLOW}构建Docker镜像...${NC}"

# 尝试标准Dockerfile
if docker build -t $IMAGE_NAME:$VERSION .; then
    echo -e "${GREEN}✅ 标准Dockerfile构建成功${NC}"
elif docker build -f Dockerfile.working -t $IMAGE_NAME:$VERSION .; then
    echo -e "${GREEN}✅ Dockerfile.working构建成功${NC}"
elif docker build -f Dockerfile.simple -t $IMAGE_NAME:$VERSION .; then
    echo -e "${GREEN}✅ Dockerfile.simple构建成功${NC}"
else
    echo -e "${RED}❌ 所有Dockerfile版本都构建失败${NC}"
    echo -e "${YELLOW}请检查 DOCKER_TROUBLESHOOTING.md 获取帮助${NC}"
    exit 1
fi

docker tag $IMAGE_NAME:$VERSION $IMAGE_NAME:latest

# 显示镜像信息
echo ""
echo -e "${BLUE}=== 镜像信息 ===${NC}"
docker images | grep $IMAGE_NAME

# 询问是否导出镜像
echo ""
read -p "是否导出镜像到文件? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    OUTPUT_FILE="${IMAGE_NAME}_${VERSION}.tar"
    echo -e "${YELLOW}导出镜像到 $OUTPUT_FILE...${NC}"
    docker save -o $OUTPUT_FILE $IMAGE_NAME:$VERSION
    
    # 压缩镜像
    echo -e "${YELLOW}压缩镜像文件...${NC}"
    gzip $OUTPUT_FILE
    COMPRESSED_FILE="${OUTPUT_FILE}.gz"
    
    echo -e "${GREEN}✅ 镜像已导出: $COMPRESSED_FILE${NC}"
    echo -e "${BLUE}文件大小: $(du -h $COMPRESSED_FILE | cut -f1)${NC}"
fi

echo ""
echo -e "${GREEN}=== 构建完成 ===${NC}"
echo -e "${YELLOW}启动命令:${NC}"
echo "  docker-compose up -d"
echo ""
echo -e "${YELLOW}或使用docker run:${NC}"
echo "  docker run -d --name geektime_dl -v \$(pwd)/data:/app/data -v \$(pwd)/config:/app/config $IMAGE_NAME:$VERSION"