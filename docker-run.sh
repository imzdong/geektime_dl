#!/bin/bash

# docker-run.sh - 简化的Docker运行脚本（不依赖docker-compose）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="geektime_dl"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

show_help() {
    echo -e "${GREEN}geektime_dl Docker运行脚本${NC}"
    echo ""
    echo "用法: $0 [build|run|shell|clean|help] [参数]"
    echo ""
    echo "命令:"
    echo "  build                    - 构建Docker镜像"
    echo "  run [命令]               - 运行geektime命令"
    echo "  shell                    - 进入容器shell"
    echo "  clean                    - 清理Docker镜像"
    echo "  help                     - 显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 build                 # 构建镜像"
    echo "  $0 run query             # 查询课程"
    echo "  $0 run ebook 48          # 下载课程48"
    echo "  $0 run ebook 48 --comments-count 50"
    echo "  $0 shell                 # 进入容器"
    echo ""
    echo "目录映射:"
    echo "  ./output  -> /app/output   (下载文件)"
    echo "  ./config  -> /app/config   (配置文件)"
    echo "  ./cache   -> /app/cache    (缓存文件)"
}

setup_dirs() {
    echo -e "${YELLOW}设置目录...${NC}"
    mkdir -p "$SCRIPT_DIR/output" "$SCRIPT_DIR/config" "$SCRIPT_DIR/cache"
    
    # 复制配置文件模板
    CONFIG_FILE="$SCRIPT_DIR/config/geektime.cfg"
    if [ ! -f "$CONFIG_FILE" ] && [ -f "$SCRIPT_DIR/geektime.cfg.example" ]; then
        cp "$SCRIPT_DIR/geektime.cfg.example" "$CONFIG_FILE"
        echo -e "${GREEN}配置文件已创建: $CONFIG_FILE${NC}"
        echo -e "${YELLOW}请编辑配置文件并填入认证信息${NC}"
    fi
}

build_image() {
    echo -e "${YELLOW}构建Docker镜像...${NC}"
    cd "$SCRIPT_DIR"
    if command -v docker &> /dev/null; then
        docker build -t "$IMAGE_NAME" .
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}镜像构建成功${NC}"
        else
            echo -e "${RED}镜像构建失败${NC}"
            exit 1
        fi
    else
        echo -e "${RED}错误: Docker未安装或未运行${NC}"
        exit 1
    fi
}

run_command() {
    setup_dirs
    
    if [ $# -eq 0 ]; then
        echo -e "${RED}错误: 请指定要运行的命令${NC}"
        echo "示例: $0 run query"
        exit 1
    fi
    
    echo -e "${GREEN}执行: geektime $@${NC}"
    docker run --rm \
        -v "$SCRIPT_DIR/output:/app/output" \
        -v "$SCRIPT_DIR/config:/app/config" \
        -v "$SCRIPT_DIR/cache:/app/cache" \
        -e PYTHONUNBUFFERED=1 \
        "$IMAGE_NAME" "$@"
}

enter_shell() {
    setup_dirs
    echo -e "${GREEN}进入容器shell...${NC}"
    docker run -it --rm \
        -v "$SCRIPT_DIR/output:/app/output" \
        -v "$SCRIPT_DIR/config:/app/config" \
        -v "$SCRIPT_DIR/cache:/app/cache" \
        -w /app \
        "$IMAGE_NAME" /bin/bash
}

clean_image() {
    echo -e "${YELLOW}清理Docker镜像...${NC}"
    docker rmi "$IMAGE_NAME" 2>/dev/null || true
    echo -e "${GREEN}清理完成${NC}"
}

# 主逻辑
case "${1:-help}" in
    "build")
        setup_dirs
        build_image
        ;;
    "run")
        shift
        run_command "$@"
        ;;
    "shell")
        enter_shell
        ;;
    "clean")
        clean_image
        ;;
    "help"|*)
        show_help
        ;;
esac