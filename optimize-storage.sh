#!/bin/bash

# 优化存储结构的脚本

echo "🗂️  优化存储结构..."

# 创建按课程分类的目录结构
mkdir -p output/mobi output/epub output/pdf

# 创建临时目录结构（不挂载到宿主机）
docker exec geektime_dl mkdir -p /app/temp/mobi /app/temp/epub /app/temp/pdf

echo "✅ 存储结构优化完成"
echo ""
echo "📁 目录结构："
echo "  output/"
echo "  ├── mobi/         # MOBI格式文件"
echo "  ├── epub/         # EPUB格式文件" 
echo "  └── pdf/          # PDF格式文件"
echo ""
echo "  容器内："
echo "  /app/temp/        # 临时文件（不持久化）"
echo "  ├── mobi/"
echo "  ├── epub/"
echo "  └── pdf/"
echo "  /app/cache/       # 缓存文件"
echo "  /app/output/      # 最终输出文件"