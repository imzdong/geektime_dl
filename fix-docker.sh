#!/bin/bash

# fix-docker.sh - Docker问题快速修复脚本

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Docker问题快速修复 ===${NC}"

# 1. 诊断问题
echo -e "${YELLOW}🔍 诊断问题...${NC}"
if ! ./test-build.sh; then
    echo -e "${RED}❌ 发现构建问题${NC}"
fi

# 2. 清理Docker环境
echo -e "${YELLOW}🧹 清理Docker环境...${NC}"
docker-compose down 2>/dev/null || true
docker rmi geektime_dl:latest 2>/dev/null || true
docker system prune -f

# 3. 尝试标准构建
echo -e "${YELLOW}🔨 尝试标准构建...${NC}"
if docker build -t geektime_dl .; then
    echo -e "${GREEN}✅ 标准构建成功${NC}"
    BUILD_SUCCESS=true
else
    echo -e "${RED}❌ 标准构建失败${NC}"
    BUILD_SUCCESS=false
fi

# 4. 如果失败，尝试简化构建
if [ "$BUILD_SUCCESS" = false ]; then
    echo -e "${YELLOW}🔨 尝试简化构建...${NC}"
    if docker build -f Dockerfile.simple -t geektime_dl .; then
        echo -e "${GREEN}✅ 简化构建成功${NC}"
        BUILD_SUCCESS=true
    else
        echo -e "${RED}❌ 简化构建也失败${NC}"
    fi
fi

# 5. 测试运行
if [ "$BUILD_SUCCESS" = true ]; then
    echo -e "${YELLOW}🧪 测试运行...${NC}"
    if docker run --rm geektime_dl --version; then
        echo -e "${GREEN}✅ 运行测试成功${NC}"
        
        # 6. 部署
        echo -e "${YELLOW}🚀 部署容器...${NC}"
        if ./deploy.sh; then
            echo -e "${GREEN}✅ 部署成功${NC}"
        else
            echo -e "${YELLOW}⚠️  部署失败，但镜像可用${NC}"
        fi
    else
        echo -e "${RED}❌ 运行测试失败${NC}"
    fi
fi

echo -e "${BLUE}=== 修复完成 ===${NC}"

if [ "$BUILD_SUCCESS" = true ]; then
    echo -e "${GREEN}Docker问题已解决！${NC}"
    echo -e "${YELLOW}现在可以使用：${NC}"
    echo "  docker exec geektime_dl geektime query"
    echo "  docker exec geektime_dl geektime ebook 48"
else
    echo -e "${RED}问题未解决，请查看详细的故障排除指南：${NC}"
    echo "  cat DOCKER_TROUBLESHOOTING.md"
fi