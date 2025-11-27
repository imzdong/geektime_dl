# 🔧 Docker 故障排除指南

## ❌ 常见报错及解决方案

### 1. 构建错误

#### 错误：`Error: Cannot find requirements/base.txt`
```bash
# 解决方案：确保在项目根目录构建
cd geektime_dl
ls requirements/base.txt  # 确认文件存在
docker build -t geektime_dl .
```

#### 错误：`ERROR: Command errored out with exit status 1` (pip install失败)
```bash
# 解决方案：清理pip缓存重新构建
docker builder prune
docker build --no-cache -t geektime_dl .
```

#### 错误：`failed to solve: process "/bin/sh -c pip install -e ." didn't complete`
```bash
# 使用简化的Dockerfile构建
docker build -f Dockerfile.simple -t geektime_dl .
```

### 2. 运行时错误

#### 错误：`geektime: command not found`
```bash
# 解决方案：使用python模块方式运行
docker exec geektime_dl python -m geektime_dl query

# 或者进入容器
docker exec -it geektime_dl bash
python geektime.py query
```

#### 错误：`Permission denied` (权限问题)
```bash
# 修改目录权限
sudo chown -R $USER:$USER data config cache

# 或在docker run中指定用户
docker run --user $(id -u):$(id -g) ...
```

### 3. 配置文件错误

#### 错误：`File not found: config/geektime.cfg`
```bash
# 复制配置文件模板
cp geektime.cfg.example config/geektime.cfg

# 编辑配置文件
nano config/geektime.cfg
```

### 4. 网络错误

#### 错误：`Connection timeout` 或 `SSL error`
```bash
# 使用host网络模式
docker run --network host ...

# 或设置代理
docker run -e HTTP_PROXY=http://proxy:port ...
```

## 🔍 调试方法

### 1. 查看详细构建日志
```bash
docker build --no-cache --progress=plain -t geektime_dl .
```

### 2. 进入容器调试
```bash
docker run -it --entrypoint /bin/bash geektime_dl
# 在容器内手动测试
python -m geektime_dl --help
```

### 3. 检查容器日志
```bash
docker logs geektime_dl
docker logs -f geektime_dl  # 实时查看
```

### 4. 验证安装
```bash
# 检查geektime是否正确安装
docker exec geektime_dl which geektime
docker exec geektime_dl python -c "import geektime_dl; print('OK')"
```

## 🛠️ 修复脚本

### 自动诊断脚本
```bash
#!/bin/bash
# diagnose.sh - Docker问题诊断脚本

echo "=== Docker问题诊断 ==="

# 1. 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装"
    exit 1
fi

# 2. 检查文件
echo "检查必要文件..."
files=("Dockerfile" "requirements/base.txt" "setup.py" "geektime.py")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 缺失"
    fi
done

# 3. 检查权限
echo "检查目录权限..."
dirs=("data" "config" "cache")
for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        if [ -w "$dir" ]; then
            echo "✅ $dir 可写"
        else
            echo "❌ $dir 不可写"
        fi
    else
        echo "📝 $dir 不存在，将自动创建"
        mkdir -p "$dir"
    fi
done

echo "=== 诊断完成 ==="
```

## 🔄 重新构建流程

### 完全清理重建
```bash
# 1. 停止并删除容器
docker-compose down
docker rm -f geektime_dl 2>/dev/null || true

# 2. 删除镜像
docker rmi geektime_dl:latest 2>/dev/null || true

# 3. 清理缓存
docker system prune -f

# 4. 重新构建
docker build --no-cache -t geektime_dl .

# 5. 重新启动
docker-compose up -d
```

### 使用简化版本
```bash
# 如果主Dockerfile有问题，使用简化版本
docker build -f Dockerfile.simple -t geektime_dl .
docker-compose up -d
```

## 📞 获取帮助

如果以上方法都无法解决问题：

1. **查看详细错误信息**：
   ```bash
   docker build --progress=plain . 2>&1 | tee build-error.log
   ```

2. **提供错误信息时请包括**：
   - Docker版本 (`docker --version`)
   - 完整的错误日志
   - 操作系统类型
   - 使用的命令

3. **测试环境**：
   ```bash
   # 使用测试脚本
   ./test-build.sh
   # 查看 build.log 获取详细信息
   ```

---

**大部分问题都可以通过清理缓存重新构建解决！** 🚀