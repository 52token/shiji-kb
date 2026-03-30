#!/bin/bash
# 启动本地HTTP服务器用于预览史记HTML

PORT=${1:-8000}

echo "启动HTTP服务器..."
echo "访问地址: http://localhost:$PORT/chapters/"
echo "按 Ctrl+C 停止服务器"
echo ""

cd docs && python3 -m http.server $PORT
