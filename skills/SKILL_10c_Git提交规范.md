---
name: skill-10c
title: Git提交规范
description: Git提交消息格式规范、提交内容管理、分支策略、代码审查流程。确保commit历史清晰可追溯、便于代码审查和问题定位。适用于版本控制、团队协作、代码管理等场景。
---

# SKILL 10c: Git提交规范 — 让每个commit都有意义

> **核心理念**：好的commit不仅记录了"做了什么"，更要说明"为什么做"、"怎么做的"。

---

## 一、基本原则

### 1.1 五大原则

1. **明确授权** - 只在用户明确要求时才执行git commit
2. **精准提交** - 只提交缓存区（staged）内容，不擅自添加未暂存文件
3. **清晰描述** - 提交消息准确描述做了什么，按模块分组
4. **原子提交** - 每个commit只做一件事，便于回滚
5. **可追溯性** - 提交消息包含足够信息，便于未来查证

### 1.2 禁止事项

❌ **绝对禁止**：

- 不要自动commit（必须用户明确要求）
- 不要擅自 `git add -A` 或 `git add .` 添加未暂存的文件
- 不要在commit message中自动添加版本号（如v3.1），版本号由用户决定
- 不要跳过pre-commit hooks（除非用户明确要求 `--no-verify`）
- 不要force push到main/master分支（除非用户明确要求且理解后果）

✅ **允许操作**：

- 在用户明确要求时创建commit
- 提交用户已暂存（git add）的文件
- 按照规范格式编写commit message
- 在commit失败时进行一次重试（如pre-commit hook修改了文件）

---

## 二、提交消息格式

### 2.1 标准格式

```
首行总结（做了什么，不超过50字）

模块A:
- 新增 xxx
- 更新 yyy

模块B:
- 修复 zzz
- 删除 www

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 2.2 格式说明

#### 首行总结

- **长度**：不超过50字（中文）或50字符（英文）
- **内容**：一句话说明做了什么（动宾结构）
- **示例**：
  - ✅ "完成001-004章多版本互校并同步派生文件"
  - ✅ "修复标注完整性检查脚本的编码问题"
  - ❌ "更新"（太笼统）
  - ❌ "今天的工作"（无意义）

#### 空行

首行总结后**必须**有一个空行，再开始详细描述。

#### 详细描述

**按模块分组**：

```
章节标注:
- 完成001_五帝本纪实体标注
- 完成002_夏本纪实体标注

反思工具:
- 新增按类型反思脚本
- 更新反思报告格式

文档:
- 更新README添加安装说明
```

**分类动词**：

| 分类 | 动词 | 示例 |
|------|------|------|
| **新增** | 新增、添加、创建 | 新增SKILL_10c文档 |
| **更新** | 更新、修改、完善、优化 | 更新实体统计脚本 |
| **修复** | 修复、修正、解决 | 修复615处人名标注错误 |
| **删除** | 删除、移除、清理 | 删除过时的临时文件 |

#### 尾注（Co-Authored-By）

当使用AI助手（如Claude Code）完成工作时，添加：

```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 2.3 HEREDOC格式传递

**重要**：为确保格式正确，commit message必须通过HEREDOC传递：

```bash
git commit -m "$(cat <<'EOF'
首行总结（做了什么）

模块A:
- 新增 xxx
- 更新 yyy

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**原因**：
- 支持多行消息
- 避免shell转义问题
- 确保换行符正确

---

## 三、提交内容管理

### 3.1 提交前检查

在执行commit前，**必须**先运行以下检查：

```bash
# 1. 查看未暂存的文件
git status

# 2. 查看已暂存的文件（将要提交的内容）
git diff --cached

# 3. 查看最近的commit历史（了解commit message风格）
git log --oneline -10
```

### 3.2 只提交已暂存内容

**原则**：commit时只提交缓存区（staged）内容，提交消息只描述缓存区中的变更。

```bash
# ❌ 错误做法
git add -A  # 添加所有未暂存文件
git commit -m "更新"

# ✅ 正确做法
# （假设用户已经手动git add了需要提交的文件）
git status  # 确认暂存区内容
git commit -m "$(cat <<'EOF'
完成001-004章实体标注

章节标注:
- 完成001_五帝本纪.tagged.md
- 完成002_夏本纪.tagged.md
- 完成003_殷本纪.tagged.md
- 完成004_周本纪.tagged.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 3.3 敏感文件检查

**禁止提交**：

- `.env` 文件（包含密钥）
- `credentials.json`（凭证文件）
- `*.key`、`*.pem`（私钥文件）
- 临时文件（`*.tmp`、`*.swp`）
- 大型二进制文件（除非必要）

**提示**：如果用户尝试提交敏感文件，应警告并询问确认。

---

## 四、提交工作流

### 4.1 标准提交流程

```bash
# 1. 查看当前状态
git status

# 2. 查看将要提交的内容
git diff --cached

# 3. 查看最近的commit历史（学习风格）
git log --oneline -10

# 4. 执行提交
git commit -m "$(cat <<'EOF'
首行总结

模块A:
- 变更1
- 变更2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# 5. 验证提交成功
git status
```

### 4.2 Pre-commit Hook处理

**场景**：Pre-commit hook修改了文件（如格式化代码）

**处理流程**：

```bash
# 1. 第一次提交失败（hook修改了文件）
git commit -m "..."
# 输出: pre-commit hook 修改了文件，请重新add

# 2. 检查是否安全amend
git log -1 --format='%an %ae'  # 检查authorship
git status  # 确认"Your branch is ahead"

# 3. 如果满足条件，amend提交
if [作者是自己] && [未push到remote]; then
    git add [hook修改的文件]
    git commit --amend --no-edit
fi

# 4. 如果不满足条件，创建新commit
else
    git add [hook修改的文件]
    git commit -m "应用pre-commit hook的格式化修改"
fi
```

**重要**：只在以下情况才使用 `--amend`：
- 作者是自己（不是其他开发者的commit）
- 未push到remote（本地commit）

### 4.3 提交失败处理

**常见错误及解决方案**：

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `nothing to commit` | 暂存区为空 | 先 `git add` 文件 |
| `pre-commit hook failed` | Hook检查失败 | 查看错误信息，修复问题后重新提交 |
| `conflict` | 合并冲突 | 解决冲突后 `git add` 并提交 |
| `permission denied` | 文件权限问题 | 检查文件权限，必要时 `chmod` |

---

## 五、提交最佳实践

### 5.1 原子提交原则

**定义**：每个commit只做一件事，便于回滚和审查。

**示例**：

```bash
# ✅ 好的原子提交
Commit 1: "新增SKILL_10c文档"
Commit 2: "修复标注完整性脚本bug"
Commit 3: "更新README添加SKILL_10c链接"

# ❌ 不好的混合提交
Commit 1: "今天的工作"
  - 新增SKILL_10c
  - 修复脚本bug
  - 更新README
  - 修复3个标注错误
```

### 5.2 提交消息质量

**优秀示例**：

```
完成001-012本纪的人名实体跨章反思

实体反思:
- 修正615处人名标注错误（邦国名/氏族名/动词误标）
- 新增跨章一致性检查规则
- 更新人名实体统计（15,190词条）

工具优化:
- 优化反思脚本性能（处理速度提升3倍）
- 新增进度条显示

文档:
- 更新SKILL_03e反思方法论
- 添加615处错误的分类统计

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**为什么优秀**：
1. 首行清晰说明做了什么
2. 按模块分组，层次清晰
3. 包含关键数字（615处、15,190词条）
4. 区分了实体反思、工具优化、文档更新
5. 动词准确（修正、新增、优化、更新）

**糟糕示例**：

```
更新

- 修改了一些文件
- 做了一些改进
```

**为什么糟糕**：
1. 首行无意义（"更新"太笼统）
2. 没有说明具体做了什么
3. 没有按模块分组
4. 动词模糊（"修改"、"改进"）

### 5.3 提交频率

**建议**：

- **小功能**：完成即提交（如修复1个bug）
- **中型功能**：阶段性提交（如完成4章标注后提交）
- **大型功能**：分阶段多次提交（如实现新SKILL，按小节提交）

**避免**：

- ❌ 一天工作结束后一次性提交所有改动
- ❌ 每改一行就提交（过于频繁）

**原则**：每个commit应该是一个逻辑完整的单元。

---

## 六、分支管理

### 6.1 分支策略

**主分支**：
- `main` - 生产分支，始终保持可用状态

**开发分支**（可选，当前项目暂未使用）：
- `develop` - 开发分支
- `feature/xxx` - 功能分支
- `fix/xxx` - 修复分支

**当前项目**：采用简化策略，直接在main分支开发。

### 6.2 分支操作规范

**创建分支**：

```bash
# 功能开发
git checkout -b feature/add-pinyin-annotation

# Bug修复
git checkout -b fix/entity-boundary-error
```

**合并分支**：

```bash
# 切换到main
git checkout main

# 合并功能分支
git merge feature/add-pinyin-annotation --no-ff

# 删除已合并分支
git branch -d feature/add-pinyin-annotation
```

**重要**：
- 使用 `--no-ff` 保留分支历史
- 合并前先pull最新代码
- 删除已合并的分支，保持整洁

---

## 七、GitHub特定规范

### 7.1 Pull Request创建

**标题格式**：

```
[类型] 简短描述

类型: FEAT/FIX/DOC/REFACTOR
```

**示例**：
```
[FEAT] 新增拼音注释功能
[FIX] 修复标注完整性检查脚本编码问题
[DOC] 完善SKILL_10项目管理文档
```

**描述格式**：

```markdown
## Summary
<1-3 bullet points>

## Changes
- 模块A: 变更说明
- 模块B: 变更说明

## Test plan
- [ ] 本地测试通过
- [ ] Lint检查通过
- [ ] 文档已更新

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### 7.2 Commit与Issue关联

**在commit message中引用Issue**：

```
修复标注完整性检查的编码问题 (#15)

工具修复:
- 修复lint_text_integrity.py的UTF-8编码问题
- 添加BOM检测和处理逻辑

测试:
- 验证001-004章节通过检查

Fixes #15

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**关键词**：
- `Fixes #N` - 此commit修复了Issue #N（自动关闭Issue）
- `Closes #N` - 此commit关闭了Issue #N
- `Refs #N` - 此commit引用了Issue #N（不自动关闭）

### 7.3 Commit Links

**在文档中链接commit**：

```markdown
已修复标注错误，见commit [abc1234]

[abc1234]: https://github.com/baojie/shiji-kb/commit/abc1234
```

或简化格式（GitHub自动识别）：

```markdown
已修复标注错误，见commit abc1234
```

---

## 八、提交检查清单

### 8.1 提交前检查

在执行commit前，确认以下事项：

- [ ] 已查看 `git status` 确认暂存区内容
- [ ] 已查看 `git diff --cached` 确认具体改动
- [ ] 已查看 `git log` 了解commit message风格
- [ ] commit message符合格式规范
- [ ] 首行总结清晰准确（不超过50字）
- [ ] 详细描述按模块分组
- [ ] 使用了准确的动词（新增/更新/修复/删除）
- [ ] 包含了Co-Authored-By（如使用AI助手）
- [ ] 未包含敏感文件（.env、credentials等）
- [ ] 是原子提交（只做一件事）

### 8.2 提交后验证

提交完成后，验证：

- [ ] `git status` 显示working tree clean
- [ ] `git log -1` 显示的commit message正确
- [ ] 必要时push到remote：`git push`

---

## 九、常见问题

### Q1: 提交了错误的文件怎么办？

**A**: 如果还未push到remote，可以修改：

```bash
# 方案1: 修改最近一次commit
git reset HEAD~1  # 撤销commit，保留改动
# 重新add正确的文件
git add 正确的文件
git commit -m "..."

# 方案2: 使用amend（仅限未push）
git reset HEAD 错误的文件  # 从暂存区移除
git commit --amend
```

**如果已push到remote**：不建议修改，创建新commit修复。

### Q2: commit message写错了怎么办？

**A**: 如果还未push：

```bash
git commit --amend -m "$(cat <<'EOF'
正确的commit message
...
EOF
)"
```

**如果已push**：不建议修改，接受错误或创建新commit说明。

### Q3: 如何撤销commit？

**A**:

```bash
# 撤销最近1次commit，保留改动
git reset HEAD~1

# 撤销最近2次commit，保留改动
git reset HEAD~2

# 完全撤销commit和改动（危险！）
git reset --hard HEAD~1
```

### Q4: 多人协作时如何避免冲突？

**A**:

1. **提交前先pull**：`git pull --rebase`
2. **频繁提交**：避免长时间不提交导致大量冲突
3. **分工明确**：不同人负责不同模块/文件
4. **及时沟通**：修改共享文件前通知团队

---

## 十、工具与脚本

### 10.1 Git别名（可选）

在 `~/.gitconfig` 中添加：

```ini
[alias]
    st = status
    co = commit
    br = branch
    last = log -1 HEAD
    unstage = reset HEAD --
    amend = commit --amend --no-edit
```

使用：
```bash
git st        # git status
git last      # 查看最后一次commit
git unstage . # 取消暂存
```

### 10.2 Commit Message模板

创建 `.gitmessage` 模板：

```
# 首行总结（不超过50字）

# 空行

# 详细描述（按模块分组）
# 模块A:
# - 新增 xxx
# - 更新 yyy

# 🤖 Generated with [Claude Code](https://claude.com/claude-code)
#
# Co-Authored-By: Claude <noreply@anthropic.com>
```

启用：
```bash
git config commit.template .gitmessage
```

---

## 十一、与其他SKILL的关系

```
SKILL_10c Git提交规范
    ├─ 输入：暂存区内容（git add后的文件）
    ├─ 输出：commit历史
    │
    ├─ 依赖：
    │   └─ SKILL_10a（Issue管理）- commit关联Issue
    │
    └─ 支撑：
        ├─ SKILL_10b（每日工作日志）- commit是日志的数据源
        └─ SKILL_10d（CHANGELOG）- commit是CHANGELOG的数据源
```

**工作流联动**：

```
Issue创建 (SKILL_10a)
    ↓
TODO任务执行 (SKILL_10a)
    ↓
代码/文档修改
    ↓
Git提交 (SKILL_10c) ← 当前
    ↓
每日工作日志 (SKILL_10b)
    ↓
CHANGELOG更新 (SKILL_10d)
```

---

## 十二、参考资源

- Git官方文档: https://git-scm.com/doc
- Conventional Commits: https://www.conventionalcommits.org/
- GitHub Flow: https://docs.github.com/en/get-started/quickstart/github-flow
- 项目Git规范: `CLAUDE.md`

---

## 结语

**好的commit不仅是代码的快照，更是项目历史的叙述。** 每个commit message都应该让未来的自己（或他人）能够快速理解：做了什么、为什么做、怎么做的。

遵守Git提交规范，让项目的每一步都有迹可循。
