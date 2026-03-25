# 史记争霸 - GitHub Pages 部署指南

## 📍 部署地址

**在线访问**: https://baojie.github.io/shiji-kb/app/game/

## 🚀 快速部署

### 一键部署脚本

在 `app/game` 目录下运行：

```bash
./deploy_to_docs.sh
```

### 手动部署步骤

如果脚本出现问题，可以手动执行以下步骤：

```bash
# 1. 创建目标目录
mkdir -p ../../docs/app/game

# 2. 复制核心文件
cp index.html ../../docs/app/game/
cp game.js ../../docs/app/game/
cp styles.css ../../docs/app/game/

# 3. 复制文档文件
cp README.md ../../docs/app/game/
cp game_design.md ../../docs/app/game/
cp 测试地址.md ../../docs/app/game/
cp 更新日志.md ../../docs/app/game/

# 4. 提交到Git
cd ../..
git add docs/app/game/
git commit -m "部署史记争霸游戏到GitHub Pages"
git push
```

## 📂 部署文件清单

部署到 `docs/app/game/` 的文件：

### 核心文件（必需）
- `index.html` - 游戏主页面
- `game.js` - 游戏逻辑
- `styles.css` - 样式表

### 文档文件（可选）
- `README.md` - 项目说明
- `game_design.md` - 游戏设计文档
- `测试地址.md` - 测试地址列表
- `更新日志.md` - 版本更新历史

## 🔄 更新流程

当你修改了游戏代码后：

```bash
# 1. 在 app/game 目录下测试
cd app/game
python3 -m http.server 8000
# 访问 http://localhost:8000 测试

# 2. 确认无误后，运行部署脚本
./deploy_to_docs.sh

# 3. 提交更新
git add docs/app/game/
git commit -m "更新游戏内容：[描述你的修改]"
git push

# 4. 等待2-5分钟后访问线上版本
# https://baojie.github.io/shiji-kb/app/game/
```

## 🧪 本地测试

### 测试源文件
```bash
cd app/game
python3 -m http.server 8000
```
访问: http://localhost:8000

### 测试部署后的文件
```bash
cd docs/app/game
python3 -m http.server 8001
```
访问: http://localhost:8001

## 📋 部署检查清单

部署前确保：

- [ ] 所有核心文件存在（index.html, game.js, styles.css）
- [ ] 本地测试通过，游戏可以正常运行
- [ ] 没有控制台错误
- [ ] 所有章节都能正常加载
- [ ] 技能卡片显示正确
- [ ] 文件路径都是相对路径

部署后检查：

- [ ] 文件已复制到 `docs/app/game/`
- [ ] Git状态显示新文件
- [ ] 提交并推送成功
- [ ] 等待5分钟后访问线上地址
- [ ] 线上版本功能正常

## 🐛 常见问题

### Q1: 部署后访问404
**A**:
- 检查GitHub仓库的Pages设置是否启用
- 确认分支是 `main` 且目录是 `docs`
- 等待5-10分钟让GitHub Pages构建

### Q2: 页面显示但样式错乱
**A**:
- 检查CSS文件是否正确复制
- 确认index.html中的CSS路径是相对路径
- 清除浏览器缓存后重试

### Q3: 脚本运行失败
**A**:
- 确保在 `app/game` 目录下运行
- 检查脚本是否有执行权限：`chmod +x deploy_to_docs.sh`
- 使用手动部署步骤

### Q4: 更新后线上没变化
**A**:
- 确认git push成功
- 等待5-10分钟
- 强制刷新浏览器（Ctrl+Shift+R）
- 检查GitHub Actions是否构建成功

## 🔗 相关链接

- **游戏源码**: `/app/game/`
- **部署目录**: `/docs/app/game/`
- **在线地址**: https://baojie.github.io/shiji-kb/app/game/
- **主项目**: https://baojie.github.io/shiji-kb/

## 📝 版本历史

- **v0.1** (2026-02-06) - 初始版本
- **v0.2** (2026-03-25) - 修复章节结构，添加部署脚本

## 💡 提示

1. **开发时**在 `app/game/` 目录工作
2. **部署时**使用脚本自动复制到 `docs/app/game/`
3. **不要**直接修改 `docs/app/game/` 中的文件
4. 每次重大更新后记得更新版本号

---

**祝部署顺利！** 🎮
