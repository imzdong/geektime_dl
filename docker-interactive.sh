#!/bin/bash

# GeekTime DL Docker 交互式脚本
# 提供更好的容器内交互体验

CONTAINER_NAME="geektime_dl"
IMAGE_TAG="geektime_dl:enhanced"

case "$1" in
    start)
        echo "启动 GeekTime DL 增强版容器..."
        if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
            echo "✅ 容器已在运行"
        else
            docker run -d --name $CONTAINER_NAME \
                -v $(pwd)/data:/app/data \
                -v $(pwd)/config:/app/config \
                -v $(pwd)/cache:/app/cache \
                $IMAGE_TAG
            echo "✅ 容器已启动"
        fi
        echo ""
        echo "🚀 进入容器:"
        echo "  $0 enter"
        echo ""
        echo "📋 在容器内可使用命令:"
        echo "  /app/geektime query    # 查询课程"
        echo "  /app/geektime ebook 48 # 下载课程"
        echo "  /app/geektime login    # 登录"
        echo ""
        ;;
    enter)
        echo "🎓 进入 GeekTime DL 容器..."
        echo "💡 提示: 使用 'exit' 退出容器"
        echo ""
        docker exec -it $CONTAINER_NAME /bin/bash
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
        echo "执行命令: docker exec $CONTAINER_NAME $@"
        docker exec $CONTAINER_NAME "$@"
        ;;
    query)
        echo "查询课程列表..."
        docker exec -it $CONTAINER_NAME /app/geektime query --config /app/config/geektime.cfg --auth-type token --no-login
        ;;
    ebook)
        shift
        if [ -z "$1" ]; then
            echo "请指定课程ID"
            echo "用法: $0 ebook <course_id> [options]"
            exit 1
        fi
        echo "下载课程: $1"
        docker exec -it $CONTAINER_NAME /app/geektime ebook "$@" --config /app/config/geektime.cfg --auth-type token --no-login
        ;;
    *)
        echo "🎓 GeekTime DL Docker 管理工具"
        echo ""
        echo "使用方法: $0 {start|enter|stop|restart|status|exec|query|ebook}"
        echo ""
        echo "命令说明:"
        echo "  start   - 启动增强版容器"
        echo "  enter   - 进入容器shell (推荐使用)"
        echo "  stop    - 停止并删除容器"
        echo "  restart - 重启容器"
        echo "  status  - 查看容器状态"
        echo "  exec    - 执行任意命令"
        echo "  query   - 快速查询课程"
        echo "  ebook   - 快速下载课程"
        echo ""
        echo "🎯 推荐使用流程:"
        echo "  1. $0 start          # 启动容器"
        echo "  2. $0 enter          # 进入容器"
        echo "  3. /app/geektime query          # 在容器内查询"
        echo "  4. /app/geektime ebook 48        # 在容器内下载"
        echo ""
        echo "💡 在容器内可以创建别名:"
        echo "  alias gt='/app/geektime'"
        echo "  alias gq='/app/geektime query --config /app/config/geektime.cfg --auth-type token --no-login'"
        echo "  alias ge='/app/geektime ebook --config /app/config/geektime.cfg --auth-type token --no-login'"
        echo ""
        echo "📁 目录说明:"
        echo "  data/    - 下载的电子书文件"
        echo "  config/  - 配置文件 (需要geektime.cfg)"
        echo "  cache/   - 缓存文件"
        echo ""
        echo "💡 快捷命令示例:"
        echo "  $0 query               # 直接查询课程"
        echo "  $0 ebook 48 --comments-count 50  # 直接下载课程"
        exit 1
        ;;
esac