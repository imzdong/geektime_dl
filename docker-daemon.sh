#!/bin/bash

# GeekTime DL Docker 守护进程脚本
# 用于管理后台运行的geektime_dl容器

CONTAINER_NAME="geektime_dl"
IMAGE_TAG="geektime_dl:simple"

case "$1" in
    start)
        echo "启动 GeekTime DL 后台容器..."
        if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
            echo "容器已在运行"
        else
            docker run -d --name $CONTAINER_NAME \
                -v $(pwd)/data:/app/data \
                -v $(pwd)/config:/app/config \
                -v $(pwd)/cache:/app/cache \
                $IMAGE_TAG
            echo "容器已启动"
        fi
        ;;
    stop)
        echo "停止 GeekTime DL 容器..."
        docker stop $CONTAINER_NAME 2>/dev/null || echo "容器未运行"
        docker rm $CONTAINER_NAME 2>/dev/null || echo "容器已删除"
        ;;
    restart)
        echo "重启 GeekTime DL 容器..."
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
            echo "✅ 容器正在运行"
            docker ps -f name=$CONTAINER_NAME
        else
            echo "❌ 容器未运行"
        fi
        ;;
    exec)
        shift
        echo "执行命令: docker exec $CONTAINER_NAME python /app/geektime_cmd.py $@"
        docker exec $CONTAINER_NAME python /app/geektime_cmd.py "$@"
        ;;
    shell)
        echo "进入容器shell..."
        docker exec -it $CONTAINER_NAME /bin/bash
        ;;
    logs)
        docker logs -f $CONTAINER_NAME
        ;;
    *)
        echo "使用方法: $0 {start|stop|restart|status|exec|shell|logs}"
        echo ""
        echo "命令说明:"
        echo "  start   - 启动后台容器"
        echo "  stop    - 停止并删除容器"
        echo "  restart - 重启容器"
        echo "  status  - 查看容器状态"
        echo "  exec    - 执行geektime命令 (例如: $0 exec query)"
        echo "  shell   - 进入容器shell"
        echo "  logs    - 查看容器日志"
        echo ""
        echo "示例:"
        echo "  $0 start                           # 启动容器"
        echo "  $0 exec query --config /app/config/geektime.cfg --auth-type token --no-login"
        echo "  $0 exec ebook 48 --config /app/config/geektime.cfg --auth-type token --no-login --comments-count 50"
        exit 1
        ;;
esac