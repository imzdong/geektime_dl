# Docker 使用指南

## 快速开始

### 1. 构建Docker镜像

```bash
# 直接构建
docker build -t geektime_dl .

# 或使用docker-compose构建
docker-compose build
```

### 2. 准备配置文件

在宿主机创建配置文件目录并放入配置：

```bash
# 创建必要的目录
mkdir -p config output cache

# 复制配置文件模板
cp geektime.cfg.example config/geektime.cfg

# 编辑配置文件，填入你的认证信息
nano config/geektime.cfg
```

### 3. 使用方式

#### 方式一：直接使用docker命令

```bash
# 显示帮助
docker run --rm -v $(pwd)/output:/app/output -v $(pwd)/config:/app/config geektime_dl

# 查询课程
docker run --rm \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  geektime_dl query

# 下载课程（ID: 48）
docker run --rm \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  geektime_dl ebook 48 --comments-count 50

# 下载课程并设置缓存
docker run --rm \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/cache:/app/cache \
  geektime_dl ebook 48
```

#### 方式二：使用docker-compose

```bash
# 启动容器并进入交互模式
docker-compose run --rm geektime

# 下载课程
docker-compose run --rm geektime ebook 48 --comments-count 50

# 使用专用的下载服务
docker-compose --profile downloader run --rm downloader ebook 48
```

#### 方式三：创建便捷脚本

创建脚本文件 `geektime-docker.sh`：

```bash
#!/bin/bash
# geektime-docker.sh

docker run --rm \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/cache:/app/cache \
  geektime_dl "$@"
```

使用脚本：
```bash
chmod +x geektime-docker.sh
./geektime-docker.sh query
./geektime-docker.sh ebook 48 --comments-count 50
```

## 目录说明

- `output/` - 下载的电子书文件（映射到容器的 `/app/output`）
- `config/` - 配置文件目录（映射到容器的 `/app/config`）
- `cache/` - 缓存目录，支持断点续传（映射到容器的 `/app/cache`）

## 配置文件

将 `geektime.cfg` 放在 `config/` 目录下，包含你的认证信息：

```ini
[default]
area = 86
auth_token = your_auth_token_here
auth_type = token
comments_count = 50
output_folder = /app/output  # 容器内路径
```

## 常用命令示例

```bash
# 查询所有课程
docker run --rm -v $(pwd)/config:/app/config geektime_dl query

# 下载单个课程
docker run --rm -v $(pwd)/output:/app/output -v $(pwd)/config:/app/config geektime_dl ebook 48

# 批量下载多个课程
docker run --rm \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  geektime_dl ebook 48 101 102

# 下载特定格式
docker run --rm \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  geektime_dl ebook 48 --format epub

# 设置评论数量
docker run --rm \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  geektime_dl ebook 48 --comments-count 100
```

## 高级用法

### 自定义配置目录

```bash
docker run --rm \
  -v /path/to/my/output:/app/output \
  -v /path/to/my/config:/app/config \
  geektime_dl ebook 48
```

### 使用环境变量

```bash
docker run --rm \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  -e GEEKTIME_OUTPUT_DIR=/custom/output \
  geektime_dl ebook 48
```

### 后台运行（如果需要长时间下载）

```bash
docker-compose up -d downloader
docker-compose logs -f downloader
```

## 故障排除

### 权限问题
如果遇到权限问题，可以：
```bash
# 修改目录权限
sudo chown -R $USER:$USER output config cache
# 或在docker中指定用户ID
docker run --rm --user $(id -u):$(id -g) -v $(pwd)/output:/app/output geektime_dl
```

### 网络问题
如果遇到网络问题，可以：
```bash
# 使用host网络模式
docker run --rm --network host -v $(pwd)/output:/app/output geektime_dl ebook 48
```

### 清理容器
```bash
# 清理所有相关容器和镜像
docker-compose down --rmi all
docker system prune -f
```