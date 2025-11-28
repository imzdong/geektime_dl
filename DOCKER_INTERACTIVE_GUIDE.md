# Docker 交互式使用指南

## 🎯 快速开始

### 1. 启动容器

```bash
# 启动后台容器
./docker-interactive.sh start
```

### 2. 进入容器

```bash
# 进入容器交互模式
./docker-interactive.sh enter
```

## 🚀 在容器内部使用命令

进入容器后，你可以直接使用以下命令：

### 基础命令
```bash
# 现在可以直接使用geektime命令（已修复）
geektime query
geektime ebook 48
geektime login

# 或者使用完整路径
/app/geektime query
/app/geektime ebook 48
/app/geektime login

# 查看帮助
geektime help
```

### 使用内置别名（推荐）

容器启动时已自动创建别名，可以直接使用：

```bash
# 使用已创建的别名
gq                    # 查询课程
ge 48                 # 下载课程48
ge 48 --comments-count 50  # 下载课程48，包含50条评论
gt query              # 使用别名查询
gt ebook 48           # 使用别名下载

# 手动创建更多别名（可选）
alias gt='geektime'
alias gq='geektime query --config /app/config/geektime.cfg --auth-type token --no-login'
alias ge='geektime ebook --config /app/config/geektime.cfg --auth-type token --no-login'
```

## 📋 常用操作示例

### 查询课程列表
```bash
# 直接使用geektime命令（已修复PATH问题）
geektime query --config /app/config/geektime.cfg --auth-type token --no-login

# 使用别名
gq

# 使用gt别名
gt query
```

### 下载课程
```bash
# 直接使用geektime命令
geektime ebook 48 --config /app/config/geektime.cfg --auth-type token --no-login

# 下载课程48，包含50条评论
geektime ebook 48 --config /app/config/geektime.cfg --auth-type token --no-login --comments-count 50

# 使用别名
ge 48
ge 48 --comments-count 50

# 使用gt别名
gt ebook 48
gt ebook 48 --comments-count 50
```

### 下载多个课程
```bash
# 下载多个课程
/app/geektime ebook 48 49 50 --config /app/config/geektime.cfg --auth-type token --no-login

# 使用别名（需要先修改别名定义）
ge 48 49 50
```

## 🛠️ 容器管理脚本

`docker-interactive.sh` 提供了完整的管理功能：

```bash
# 启动容器
./docker-interactive.sh start

# 进入容器
./docker-interactive.sh enter

# 快速查询（不进入容器）
./docker-interactive.sh query

# 快速下载（不进入容器）
./docker-interactive.sh ebook 48 --comments-count 50

# 查看容器状态
./docker-interactive.sh status

# 停止容器
./docker-interactive.sh stop

# 重启容器
./docker-interactive.sh restart

# 执行任意命令
./docker-interactive.sh exec ls -la /app/data
```

## 📁 目录说明

容器内的目录映射到宿主机：

- `/app/data` ←→ `./data` (下载的电子书文件)
- `/app/config` ←→ `./config` (配置文件目录)
- `/app/cache` ←→ `./cache` (缓存文件)

## 🔧 配置文件

确保 `./config/geektime.cfg` 文件包含正确的认证信息：

```ini
[default]
area = 86
auth_token = your_auth_token_here
auth_type = token
comments_count = 50
output_folder = /app/data
```

## 💡 使用技巧

### 1. 持久化别名
在容器内创建的别名会在退出后失效。要永久保存，可以：

```bash
# 编辑 .bashrc 文件
echo "alias gt='/app/geektime'" >> ~/.bashrc
echo "alias gq='/app/geektime query --config /app/config/geektime.cfg --auth-type token --no-login'" >> ~/.bashrc
echo "alias ge='/app/geektime ebook --config /app/config/geektime.cfg --auth-type token --no-login'" >> ~/.bashrc

# 重新加载配置
source ~/.bashrc
```

### 2. 查看下载进度
```bash
# 在另一个终端中查看下载进度
docker logs -f geektime_dl
```

### 3. 直接操作宿主机文件
下载的文件直接保存在宿主机的 `./data` 目录中，可以直接在宿主机查看和使用。

## 🎯 推荐工作流程

1. **一次性设置**：
   ```bash
   # 启动容器
   ./docker-interactive.sh start
   
   # 进入容器
   ./docker-interactive.sh enter
   
   # 在容器内创建别名
   alias gt='/app/geektime'
   alias gq='/app/geektime query --config /app/config/geektime.cfg --auth-type token --no-login'
   alias ge='/app/geektime ebook --config /app/config/geektime.cfg --auth-type token --no-login'
   ```

2. **日常使用**：
   ```bash
   # 进入容器
   ./docker-interactive.sh enter
   
   # 查询课程
   gq
   
   # 下载感兴趣的课程
   ge 48 --comments-count 50
   
   # 退出容器
   exit
   ```

3. **或者使用快捷命令**（不进入容器）：
   ```bash
   ./docker-interactive.sh query
   ./docker-interactive.sh ebook 48 --comments-count 50
   ```

## 🆘 故障排除

### 容器无法启动
```bash
# 检查镜像是否存在
docker images | grep geektime_dl

# 如果不存在，重新构建
docker build -f Dockerfile.enhanced -t geektime_dl:enhanced .
```

### 命令无法执行
```bash
# 检查配置文件
./docker-interactive.sh exec ls -la /app/config/

# 检查geektime脚本
./docker-interactive.sh exec ls -la /app/geektime
```

### 认证失败
确保 `./config/geektime.cfg` 文件中的 `auth_token` 是有效的，并且使用 `--auth-type token --no-login` 参数。

---

这样你就可以像使用原生命令一样在Docker容器内使用geektime_dl了！