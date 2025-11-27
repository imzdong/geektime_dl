.PHONY: help build run query ebook clean docker-clean setup

# 默认目标
help:
	@echo "geektime_dl Docker版本 - 使用指南"
	@echo ""
	@echo "可用命令:"
	@echo "  make build        - 构建Docker镜像"
	@echo "  make setup        - 初始化配置和环境"
	@echo "  make query        - 查询所有课程"
	@echo "  make ebook ID=48  - 下载指定课程"
	@echo "  make run CMD='查询命令' - 执行自定义命令"
	@echo "  make clean        - 清理临时文件"
	@echo "  make docker-clean - 清理Docker相关资源"
	@echo ""
	@echo "示例:"
	@echo "  make ebook ID=48"
	@echo "  make run CMD='ebook 48 --comments-count 50'"
	@echo "  make run CMD='query'"

# 构建Docker镜像
build:
	@echo "构建Docker镜像..."
	docker build -t geektime_dl .

# 初始化配置和环境
setup:
	@echo "初始化配置和环境..."
	mkdir -p output config cache
	@if [ ! -f config/geektime.cfg ]; then \
		if [ -f geektime.cfg.example ]; then \
			cp geektime.cfg.example config/geektime.cfg; \
			echo "配置文件模板已创建: config/geektime.cfg"; \
			echo "请编辑配置文件并填入你的认证信息"; \
		else \
			echo "错误: 无法找到配置文件模板"; \
		fi; \
	fi
	@chmod +x geektime-docker.sh

# 查询课程
query:
	@echo "查询所有课程..."
	./geektime-docker.sh query

# 下载课程
ebook:
	@echo "下载课程: $(ID)"
	@if [ -z "$(ID)" ]; then \
		echo "错误: 请指定课程ID"; \
		echo "用法: make ebook ID=48"; \
		exit 1; \
	fi
	./geektime-docker.sh ebook $(ID)

# 执行自定义命令
run:
	@echo "执行命令: $(CMD)"
	@if [ -z "$(CMD)" ]; then \
		echo "错误: 请指定要执行的命令"; \
		echo "用法: make run CMD='ebook 48 --comments-count 50'"; \
		exit 1; \
	fi
	./geektime-docker.sh $(CMD)

# 使用docker-compose运行
compose:
	@echo "使用docker-compose运行..."
	docker-compose run --rm geektime $(CMD)

# 构建镜像
docker-build:
	docker-compose build

# 清理临时文件
clean:
	@echo "清理临时文件..."
	@find . -name "*.log" -delete 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf output/* cache/* 2>/dev/null || true

# 清理Docker相关资源
docker-clean:
	@echo "清理Docker相关资源..."
	docker-compose down --rmi all 2>/dev/null || true
	docker system prune -f

# 完全清理
distclean: clean docker-clean
	@echo "完全清理..."

# 开发模式 - 进入容器shell
shell:
	docker run -it --rm \
		-v $(PWD)/output:/app/output \
		-v $(PWD)/config:/app/config \
		-v $(PWD)/cache:/app/cache \
		geektime_dl /bin/bash

# 查看日志
logs:
	docker-compose logs -f

# 快速测试
test: build
	@echo "测试Docker镜像..."
	docker run --rm geektime_dl --version

# 显示Docker信息
docker-info:
	docker images | grep geektime_dl
	docker ps -a | grep geektime

# 实用命令集合
examples:
	@echo "常用示例:"
	@echo "  make setup                    # 初始化配置"
	@echo "  make query                    # 查询课程"
	@echo "  make ebook ID=48              # 下载课程48"
	@echo "  make run CMD='ebook 48 --comments-count 50'  # 下载课程48并设置评论数量"
	@echo "  make run CMD='ebook 48 101 102'  # 批量下载多个课程"
	@echo "  make run CMD='ebook 48 --format epub'  # 下载EPUB格式"
	@echo "  make shell                    # 进入容器shell"