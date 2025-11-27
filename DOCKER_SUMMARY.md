# 🐳 Docker 完整工作流总结

## ✅ 现在你可以使用标准Docker命令了！

### 📦 构建镜像
```bash
docker build -t geektime_dl:latest .
# 或
./build.sh
```

### 🚀 启动容器
```bash
docker-compose up -d
# 或
docker run -d --name geektime_dl \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/cache:/app/cache \
  geektime_dl:latest
```

### 📤 分享镜像到其他电脑
```bash
# 导出镜像
docker save -o geektime_dl.tar geektime_dl:latest

# 在其他电脑导入
docker load -i geektime_dl.tar

# 启动
docker-compose up -d
```

### 🔄 容器管理
```bash
# 查看状态
docker ps | grep geektime_dl

# 查看日志
docker logs geektime_dl

# 进入容器
docker exec -it geektime_dl bash

# 停止容器
docker stop geektime_dl

# 启动容器
docker start geektime_dl

# 删除容器
docker rm geektime_dl
```

### 📱 下载课程
```bash
# 查询课程
docker exec geektime_dl geektime query

# 下载课程
docker exec geektime_dl geektime ebook 48 --comments-count 50

# 查看下载结果
ls -la data/
```

## 🗂️ 目录结构
```
geektime_dl/
├── data/           # 下载的电子书 (宿主机 -> 容器 /app/data)
├── config/         # 配置文件 (宿主机 -> 容器 /app/config)
├── cache/          # 缓存文件 (宿主机 -> 容器 /app/cache)
├── Dockerfile      # 镜像定义
├── docker-compose.yml  # 容器配置
├── build.sh        # 构建脚本
├── deploy.sh       # 部署脚本
└── ...             # 其他文件
```

## 🎯 一键命令
```bash
# 完整部署流程
git clone https://github.com/jachinlin/geektime_dl.git
cd geektime_dl
./build.sh    # 构建镜像
./deploy.sh   # 部署容器
docker exec geektime_dl geektime ebook 48 --comments-count 50
```

## 📚 详细文档
- [DOCKER_INSTALL.md](DOCKER_INSTALL.md) - 详细安装指南
- [DOCKER_USAGE.md](DOCKER_USAGE.md) - 使用说明
- [README.md](README.md) - 项目说明

---

**现在你完全可以用标准Docker命令来管理geektime_dl了！** 🎉