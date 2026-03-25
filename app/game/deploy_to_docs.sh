#!/bin/bash

# 史记争霸 - 部署到 shiji-kb GitHub Pages
# 部署目标: https://baojie.github.io/shiji-kb/app/game/

set -e  # 遇到错误立即退出

echo "🎮 史记争霸 - 部署到 GitHub Pages"
echo "=================================="
echo ""

# 检查是否在game目录
if [ ! -f "game.js" ] || [ ! -f "index.html" ]; then
    echo "❌ 错误：请在 app/game 目录下运行此脚本"
    exit 1
fi

# 检查docs目录是否存在
if [ ! -d "../../docs" ]; then
    echo "❌ 错误：找不到 docs 目录"
    exit 1
fi

echo "📦 准备部署..."

# 创建目标目录
TARGET_DIR="../../docs/app/game"
mkdir -p "$TARGET_DIR"

echo "📂 复制文件到 docs/app/game/ ..."

# 复制核心文件
cp index.html "$TARGET_DIR/"
cp game.js "$TARGET_DIR/"
cp styles.css "$TARGET_DIR/"

# 复制文档文件（如果存在）
[ -f "README.md" ] && cp README.md "$TARGET_DIR/"
[ -f "game_design.md" ] && cp game_design.md "$TARGET_DIR/"
[ -f "测试地址.md" ] && cp 测试地址.md "$TARGET_DIR/"
[ -f "更新日志.md" ] && cp 更新日志.md "$TARGET_DIR/"

# 创建 .nojekyll 文件（如果不存在）
if [ ! -f "../../docs/.nojekyll" ]; then
    echo "📝 创建 .nojekyll 文件..."
    touch ../../docs/.nojekyll
fi

echo ""
echo "✅ 文件复制完成！"
echo ""
echo "📊 已复制的文件："
ls -lh "$TARGET_DIR/" | grep -E "\.(html|css|js|md)$"
echo ""

# 检查git状态
cd ../..
echo "📋 Git 状态："
git status docs/app/game/
echo ""

echo "=========================================="
echo "  部署准备完成！"
echo "=========================================="
echo ""
echo "下一步操作："
echo "  1. 检查文件是否正确："
echo "     ls -la docs/app/game/"
echo ""
echo "  2. 测试本地文件（可选）："
echo "     cd docs/app/game && python3 -m http.server 8000"
echo "     然后访问: http://localhost:8000"
echo ""
echo "  3. 提交到Git："
echo "     git add docs/app/game/"
echo "     git commit -m \"部署史记争霸游戏到GitHub Pages\""
echo "     git push"
echo ""
echo "  4. 等待几分钟后访问："
echo "     https://baojie.github.io/shiji-kb/app/game/"
echo ""
