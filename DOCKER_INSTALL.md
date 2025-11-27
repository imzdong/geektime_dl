# Docker 安装和使用指南

## 🐳 标准 Docker 工作流

### 1. 📥 下载源码

```bash
git clone https://github.com/jachinlin/geektime_dl.git
cd geektime_dl
```

### 2. 🔨 构建 Docker 镜像

```bash
# 方式一：使用 docker build
docker build -t geektime_dl:latest .

# 方式二：使用 docker-compose（推荐）
docker-compose build
```

### 3. 🚀 启动容器

```bash
# 方式一：使用 docker run
docker run -d --name geektime_dl \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/cache:/app/cache \
  geektime_dl:latest

# 方式二：使用 docker-compose（推荐）
docker-compose up -d
```

### 4. 🛠️ 使用容器

```bash
# 查看容器状态
docker ps | grep geektime

# 进入容器交互模式
docker exec -it geektime_dl bash

# 在容器中执行命令
docker exec geektime_dl geektime query
docker exec geektime_dl geektime ebook 48 --comments-count 50
```

## 📦 分享镜像到其他电脑

### 导出镜像

```bash
# 导出镜像到文件
docker save -o geektime_dl.tar geektime_dl:latest

# 压缩镜像（可选）
gzip geektime_dl.tar
```

### 在其他电脑上导入

```bash
# 解压（如果压缩了）
gunzip geektime_dl.tar.gz

# 导入镜像
docker load -i geektime_dl.tar

# 验证镜像
docker images | grep geektime_dl
```

### 推送到镜像仓库（可选）

```bash
# 标记镜像
docker tag geektime_dl:latest your-registry/geektime_dl:latest

# 推送到私有仓库
docker push your-registry/geektime_dl:latest

# 推送到 Docker Hub
docker tag geektime_dl:latest yourusername/geektime_dl:latest
docker push yourusername/geektime_dl:latest
```

## 🔧 常用 Docker 命令

### 镜像操作

```bash
# 查看镜像
docker images | grep geektime

# 删除镜像
docker rmi geektime_dl:latest

# 重新构建镜像
docker-compose build --no-cache
```

### 容器操作

```bash
# 启动容器
docker-compose start geektime

# 停止容器
docker-compose stop geektime

# 重启容器
docker-compose restart geektime

# 删除容器
docker-compose down

# 查看日志
docker-compose logs geektime

# 实时查看日志
docker-compose logs -f geektime
```

## 📁 目录结构

```
geektime_dl/
├── data/           # 下载的电子书文件
├── config/         # 配置文件
├── cache/          # 缓存文件
├── Dockerfile      # Docker镜像定义
├── docker-compose.yml  # Docker Compose配置
└── ...             # 其他项目文件
```

## ⚙️ 配置文件设置

1. **创建配置文件**
```bash
mkdir -p config
cp geektime.cfg.example config/geektime.cfg
```

2. **编辑配置文件**
```bash
nano config/geektime.cfg
```

3. **配置文件内容**
```ini
[default]
area = 86
auth_token = your_auth_token_here
auth_type = token
comments_count = 50
output_folder = /app/data
```

## 🚀 快速使用示例

### 查询课程

```bash
# 方式一：直接执行
docker exec geektime_dl geektime query

# 方式二：重新启动并执行
docker-compose run --rm geektime geektime query
```

### 下载课程

```bash
# 下载单个课程
docker exec geektime_dl geektime ebook 48 --comments-count 50

# 批量下载
docker exec geektime_dl geektime ebook 48 101 102

# 下载指定格式
docker exec geektime_dl geektime ebook 48 --format epub
```

### 查看下载结果

```bash
# 查看下载的文件
ls -la data/

# 进入数据目录
cd data/
```

## 🔍 故障排除

### 常见问题

1. **权限问题**
```bash
# 修改目录权限
sudo chown -R $USER:$USER data config cache
```

2. **容器启动失败**
```bash
# 查看详细日志
docker-compose logs geektime

# 重新构建
docker-compose build --no-cache
```

3. **镜像构建失败**
```bash
# 清理Docker缓存
docker system prune -f

# 重新构建
docker build --no-cache -t geektime_dl:latest .
```

### 性能优化

```bash
# 限制内存使用
docker run -m 512m --name geektime_dl geektime_dl

# 设置CPU限制
docker run --cpus="1.0" --name geektime_dl geektime_dl
```

## 🔄 持续运行

### 设置自动重启

```bash
# docker-compose 方式（已配置）
restart: unless-stopped

# docker run 方式
docker run -d --restart unless-stopped --name geektime_dl geektime_dl
```

### 定时任务

```bash
# 添加到 crontab
crontab -e

# 每天凌晨3点执行下载
0 3 * * * cd /path/to/geektime_dl && docker exec geektime_dl geektime ebook 48
```

## 📊 监控和日志

```bash
# 查看容器资源使用
docker stats geektime_dl

# 查看详细日志
docker inspect geektime_dl

# 导出日志
docker logs geektime_dl > geektime.log
```

## 🏁 生产环境部署

```bash
# 生产环境配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

这个标准的工作流让你可以：
1. ✅ 下载源码构建镜像
2. ✅ 导出镜像分享给其他电脑
3. ✅ 使用标准docker命令管理
4. ✅ 数据持久化存储