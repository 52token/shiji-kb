# 配置面板功能 - 更新日志

## 2026-03-30 - v1.0 初始版本

### 新增功能

#### 1. 配置面板组件
- 右上角齿轮按钮（⚙️）
- 浮动配置面板
- 语法高亮开关选项
- 状态持久化（localStorage）

#### 2. 修改的文件

**核心生成脚本**：
- `render_shiji_html.py` (第 784-816 行)
  - 在 HTML 模板中自动包含配置面板 HTML
  - 在 `</body>` 前引入 `settings-panel.js`

**样式文件**：
- `docs/css/shiji-styles.css` (第 473-605 行)
  - 齿轮按钮样式（定位在导航栏右侧）
  - 配置面板样式和动画
  - 语法高亮关闭状态的完整样式重置
  - **v1.0.1**: 补充了 `ritual`, `legal`, `quantity`, `verb-political`, `verb-economic` 的关闭样式

**JavaScript 模块**：
- `docs/js/settings-panel.js` (新建)
  - 面板切换逻辑
  - 复选框事件监听
  - localStorage 状态管理
  - 键盘快捷键（ESC 关闭）

**批量更新脚本**：
- `scripts/add_settings_panel.py` (新建)
  - 批量为现有 131 个 HTML 文件添加配置面板
- `scripts/verify_settings_panel.py` (新建)
  - 验证所有文件是否正确添加配置面板

**文档**：
- `docs/chapters/README_settings.md` (新建)
  - 功能说明文档

### 样式细节

#### 齿轮按钮
- 位置：`position: fixed; top: 27px; right: 20px;`
- 尺寸：32×32 像素
- 样式：方形，白色背景，灰色边框，圆角 4px
- 字体：16px 齿轮 emoji

#### 配置面板
- 位置：齿轮按钮下方（top: 70px）
- 尺寸：280px 宽度
- 样式：白色卡片，圆角 8px，阴影效果
- 动画：slideIn (200ms ease-out)

### 覆盖的实体类型

关闭语法高亮时，以下所有实体类型的样式都会被重置为纯文本：

**名词实体（18种）**：
- person（人名）
- place（地名）
- official（官职）
- time（时间）
- dynasty（朝代/氏族）
- feudal-state（封国/邦国）
- institution（制度）
- tribe（族群）
- artifact（器物）
- astronomy（天文/历法）
- book（典籍）
- mythical（神话/传说）
- concept（思想）
- biology（生物）
- action（行动）
- identity（身份）
- ritual（礼仪）
- legal（刑法）
- quantity（数量）

**动词实体（4种）**：
- verb-military（军事动词）
- verb-penalty（刑罚动词）
- verb-political（政治动词）
- verb-economic（经济动词）

### 技术亮点

1. **从源头解决**：修改了 `render_shiji_html.py`，未来生成的所有文件自动包含配置面板
2. **完整覆盖**：关闭语法高亮时覆盖所有 23 种实体类型（19 种名词 + 4 种动词）
3. **用户体验**：
   - 位置优化（导航栏右侧，不遮挡内容）
   - 状态持久化（localStorage 跨页面保持）
   - 平滑动画（淡入效果）
   - 多种关闭方式（点击外部、ESC 键、再次点击齿轮）
4. **样式重置彻底**：使用 `!important` 强制重置颜色、背景、下划线、加粗、字体样式等所有视觉效果

### 使用方法

1. 打开任意史记章节 HTML 文件
2. 点击导航栏右上角的齿轮图标 ⚙️
3. 在弹出面板中勾选/取消勾选"语法高亮"
4. 设置自动保存，跨页面生效

### 兼容性

- 所有现代浏览器（Chrome, Firefox, Safari, Edge）
- 移动端响应式（fixed 定位）
- localStorage API（IE 8+）

### 后续扩展

配置面板结构设计为易于扩展，可添加更多选项：
- 字体大小调节
- 行间距调节
- 实体类型过滤（只显示特定类型）
- 主题切换（日间/夜间模式）
- Purple Number 显示开关
- 实体链接显示开关

## 版本历史

- **v1.0.1** (2026-03-30): 补充遗漏的实体类型关闭样式
- **v1.0.0** (2026-03-30): 初始版本，基本功能完成
