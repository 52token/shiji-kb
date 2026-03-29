---
name: skill-10a
title: TODO和Issue管理
description: GitHub Issue分类管理与TODO任务对应流程。确保项目需求、缺陷、参考资源有序管理，与TODO任务系统联动。适用于项目管理、需求跟踪、社区协作等场景。
---

# SKILL 10a: TODO和Issue管理 — 项目任务的指挥中枢

> **核心理念**：Issue是需求的入口，TODO是执行的抓手。

---

## 一、Issue分类体系

### 1.1 七类标签

本项目使用七类标签对GitHub Issue进行分类管理：

| 标签 | 含义 | 颜色 | 典型用途 | 示例 |
|------|------|------|---------|------|
| **REF-参考** | 参考项目或资源 | 绿色 `#0E8A16` | 外部项目、论文、工具、平台 | 识典古籍、FoJin佛经平台、巴黎圣母院数字化项目 |
| **FEAT-功能建议** | 新功能建议 | 浅蓝 `#A2EEEF` | 用户需求、功能增强、新特性 | 苹果app开发、拼音注释、人物关系网 |
| **BUG-缺陷报告** | 缺陷报告 | 红色 `#D73A4A` | 错误、问题、不一致 | 标注错误、校勘问题 |
| **RES-项目资源** | 本项目资源 | 黄色 `#FBCA04` | 本项目可整合的资源 | 百衲本、三朝北盟汇编 |
| **DOC-文档维护** | 文档改进、说明完善 | 蓝色 `#0075CA` | README更新、SKILL完善、注释补充 | 完善安装文档、添加使用示例 |
| **HELP-求助** | 需要帮助或指导 | 青绿 `#008672` | 技术难题、方法咨询、资源请求 | 如何部署、寻找数据源 |
| **QA-提问** | 问题咨询、疑问讨论 | 紫色 `#D876E3` | 概念澄清、原理询问、使用疑问 | 标注规范是什么、为何这样设计 |

### 1.2 分类原则

**判断流程**：

```
Issue标题/内容
    │
    ├─ 包含"REF"或"by xxx"且为外部资源？ → REF-参考
    │
    ├─ 报告错误/问题/不一致？ → BUG-缺陷报告
    │
    ├─ 提出功能需求/建议？ → FEAT-功能建议
    │
    ├─ 本项目可用资源（古籍版本/数据）？ → RES-项目资源
    │
    ├─ 文档改进、说明完善？ → DOC-文档维护
    │
    ├─ 寻求帮助、请求指导？ → HELP-求助
    │
    └─ 提问、询问、概念澄清？ → QA-提问
```

**示例分类**：

```bash
# REF-参考
- Issue #24: "REF 17-z.com"
- Issue #27: "AI以经注经：如何拆分A文本群来注释B文本？by 周渊"

# FEAT-功能建议
- Issue #34: "开发史记知识库苹果app"
- Issue #25: "希望增加拼音注释，方便阅读"
- Issue #21: "战争路线历史地图"

# BUG-缺陷报告
- Issue #15: "校勘问题"
- Issue #12: "太多错误，作为实验性玩具还行"
- Issue #11: "标注错误"

# RES-项目资源
- Issue #23: "百衲本"
- Issue #6: "add 三朝北盟汇编 by ash"

# DOC-文档维护
- 完善README安装说明
- 添加SKILL使用示例

# HELP-求助
- Issue #14: "你留的微信号搜不到"

# QA-提问
- 标注符号的设计原理是什么？
- 为什么使用〖〗而不是[]？
```

---

## 二、Issue生命周期管理

### 2.1 Issue状态流转

```
Open（开放）
    │
    ├─ REF-参考 → 整理到 resources/references/README.md → Close（已完成）
    │
    ├─ RES-项目资源 → 评估 → 下载/整合 → Close（已完成）
    │
    ├─ FEAT-功能建议 → 评估 → 创建TODO → 开发 → Close（已完成）
    │
    ├─ BUG-缺陷报告 → 复现 → 创建TODO → 修复 → Close（已完成）
    │
    ├─ DOC-文档维护 → 创建TODO → 编写/更新文档 → Close（已完成）
    │
    ├─ HELP-求助 → 提供帮助/指导 → Close（已解决）或标记为"需要更多信息"
    │
    └─ QA-提问 → 回答问题 → Close（已回答）或转为DOC（需要文档化）
```

### 2.2 REF-参考的处理流程

**标准流程**（参见本次操作示例）：

1. **识别REF类Issue**：标题包含"REF"或明确是参考资源
2. **整理到README**：添加到 `resources/references/README.md`
   - 按类别归档（数字人文项目、古籍数字化平台、历史地图可视化等）
   - 记录关键信息（网址、开发方、核心功能、技术栈）
   - 添加"与本项目关联"说明
3. **关闭Issue并回复**：
   ```markdown
   已添加到参考文献: [resources/references/README.md](链接)

   归档位置：{分类} > {项目名称}
   ```

**示例操作**：

```bash
# 1. 创建标签（首次）
gh label create "REF-参考" --description "参考项目或资源" --color "0E8A16"

# 2. 批量分类（见下节脚本）

# 3. 关闭REF类Issue
gh issue comment 32 --body "已添加到参考文献: [resources/references/README.md](链接)\n\n归档位置：古籍数字化平台 > 巴黎圣母院数字化项目（e-NDP）"
gh issue close 32 --reason completed
```

### 2.3 FEAT/BUG的TODO对应

**原则**：每个需要执行的FEAT/BUG Issue都应对应一个或多个TODO任务。

**对应关系**：

| Issue类型 | TODO示例 | 状态同步 |
|----------|---------|---------|
| FEAT-功能建议 | "调研拼音注释方案"、"实现拼音标注" | Issue关闭 ↔ TODO全部completed |
| BUG-缺陷报告 | "复现标注错误"、"修复002_夏本纪标注" | Issue关闭 ↔ TODO全部completed |

---

## 三、批量Issue管理

### 3.1 创建标签

```bash
# 一次性创建全部七类标签
gh label create "REF-参考" --description "参考项目或资源" --color "0E8A16"
gh label create "FEAT-功能建议" --description "新功能建议" --color "A2EEEF"
gh label create "BUG-缺陷报告" --description "缺陷报告" --color "D73A4A"
gh label create "RES-项目资源" --description "本项目资源" --color "FBCA04"
gh label create "DOC-文档维护" --description "文档改进、说明完善" --color "0075CA"
gh label create "HELP-求助" --description "需要帮助或指导" --color "008672"
gh label create "QA-提问" --description "问题咨询、疑问讨论" --color "D876E3"
```

### 3.2 批量分类脚本

```bash
#!/bin/bash
# issue_classification.sh

# REF-参考 (标题包含REF或明确是参考资源)
gh issue edit 24 --add-label "REF-参考"
gh issue edit 27 --add-label "REF-参考"

# FEAT-功能建议 (功能请求)
gh issue edit 34 --add-label "FEAT-功能建议"
gh issue edit 25 --add-label "FEAT-功能建议"
gh issue edit 21 --add-label "FEAT-功能建议"
# ... 更多

# BUG-缺陷报告 (问题报告)
gh issue edit 15 --add-label "BUG-缺陷报告"
gh issue edit 12 --add-label "BUG-缺陷报告"
# ... 更多

# RES-项目资源 (本项目资源)
gh issue edit 23 --add-label "RES-项目资源"
gh issue edit 6 --add-label "RES-项目资源"

# DOC-文档维护 (文档改进)
# (待添加具体Issue)

# HELP-求助 (需要帮助)
gh issue edit 14 --add-label "HELP-求助"

# QA-提问 (问题咨询)
# (待添加具体Issue)
```

### 3.3 查看分类结果

```bash
# 按标签查看
gh issue list --label "REF-参考"
gh issue list --label "FEAT-功能建议"
gh issue list --label "BUG-缺陷报告"
gh issue list --label "RES-项目资源"

# 查看全部issue及其标签
gh issue list --state open --json number,title,labels | \
  jq -r '.[] | "\(.number)\t\(.title)\t\(.labels | map(.name) | join(", "))"' | \
  sort -n
```

**输出示例**：

```
3	字典 by 三花猫	FEAT-功能建议
5	加插图 by 元治	FEAT-功能建议
6	add 三朝北盟汇编 by ash	RES-项目资源
11	标注错误	BUG-缺陷报告
14	你留的微信号搜不到	HELP-求助
24	REF 17-z.com	REF-参考
27	AI以经注经：如何拆分A文本群来注释B文本？by 周渊	REF-参考
```

---

## 四、Issue与TODO联动

### 4.1 从Issue创建TODO

**典型流程**：

```markdown
1. 用户提交Issue #25: "希望增加拼音注释，方便阅读"
   ↓
2. 评估可行性，添加标签 "FEAT-功能建议"
   ↓
3. 创建TODO任务：
   - 调研拼音注释技术方案
   - 设计拼音标注语法
   - 实现拼音标注工具
   - 为001-012本纪添加拼音
   ↓
4. 执行TODO任务（status: pending → in_progress → completed）
   ↓
5. 全部TODO完成后，关闭Issue #25
   ↓
6. 在Issue下回复：
   "已完成拼音注释功能，见commit [abc1234]"
```

**TODO示例**：

```json
{
  "content": "调研拼音注释技术方案",
  "status": "in_progress",
  "activeForm": "调研拼音注释技术方案",
  "relatedIssue": "#25"
}
```

### 4.2 TODO任务分解原则

| Issue复杂度 | TODO数量 | 示例 |
|-----------|---------|------|
| **简单** | 1个TODO | Issue #11"标注错误" → TODO"修复002_夏本纪标注错误" |
| **中等** | 2-3个TODO | Issue #25"拼音注释" → TODO"调研方案"、"实现工具"、"标注本纪" |
| **复杂** | 5+个TODO | Issue #34"苹果app" → TODO"需求分析"、"技术选型"、"UI设计"、"数据接口"、"测试发布" |

### 4.3 TODO状态与Issue状态映射

```
TODO状态          Issue状态
────────────────────────────
全部pending      → Open (未开始)
部分in_progress  → Open (进行中)
全部completed    → Close (已完成)
```

---

## 五、实战案例

### 5.1 案例1: REF类Issue批量处理

**背景**：2026-03-29，有4个REF类Issue需要整理

**操作步骤**：

```bash
# 1. 查看REF类Issue
gh issue list --state open --limit 100 --json number,title | \
  jq -r '.[] | select(.title | test("ref"; "i")) | "\(.number)\t\(.title)"'

# 输出:
# 32	REF  巴黎圣母院数据化项
# 31	REF 识典古籍
# 30	REF  https://chinawarfare.pages.dev/
# 22	add ref

# 2. 获取详细信息并整理到README
gh issue view 32 --json title,body,url
# ... 编辑 resources/references/README.md

# 3. 关闭Issue并回复
gh issue comment 32 --body "已添加到参考文献: [resources/references/README.md](链接)\n\n归档位置：古籍数字化平台 > 巴黎圣母院数字化项目（e-NDP）"
gh issue close 32 --reason completed

# 4. 重复步骤3处理Issue #31, #30, #22
```

**结果**：4个REF类Issue全部归档并关闭，参考文献库增加4个项目

### 5.2 案例2: FEAT类Issue → TODO任务

**背景**：Issue #34 "开发史记知识库苹果app"

**TODO分解**：

```json
[
  {
    "content": "需求分析：明确app核心功能",
    "status": "pending",
    "activeForm": "需求分析：明确app核心功能"
  },
  {
    "content": "技术选型：iOS/macOS开发框架",
    "status": "pending",
    "activeForm": "技术选型：iOS/macOS开发框架"
  },
  {
    "content": "数据接口设计：知识图谱API",
    "status": "pending",
    "activeForm": "数据接口设计：知识图谱API"
  },
  {
    "content": "UI/UX设计：多维度导航界面",
    "status": "pending",
    "activeForm": "UI/UX设计：多维度导航界面"
  },
  {
    "content": "MVP开发：基础阅读器",
    "status": "pending",
    "activeForm": "MVP开发：基础阅读器"
  }
]
```

**执行流程**：

1. Issue #34创建
2. 添加标签"FEAT-功能建议"
3. 创建5个TODO任务
4. 逐步执行（pending → in_progress → completed）
5. 全部TODO完成后关闭Issue #34

### 5.3 案例3: BUG类Issue快速修复

**背景**：Issue #11 "标注错误"

**TODO分解**：

```json
[
  {
    "content": "复现Issue #11标注错误",
    "status": "in_progress",
    "activeForm": "复现Issue #11标注错误"
  },
  {
    "content": "修复标注错误",
    "status": "pending",
    "activeForm": "修复标注错误"
  },
  {
    "content": "验证修复结果",
    "status": "pending",
    "activeForm": "验证修复结果"
  }
]
```

**关闭Issue时回复**：

```markdown
已修复标注错误，见commit [abc1234]

修复内容：
- 002_夏本纪.tagged.md:195 "五子之歌" → "五子作歌"
- 通过 python scripts/lint_text_integrity.py 002 验证
```

---

## 六、工具与脚本

### 6.1 常用gh命令

```bash
# 创建Issue
gh issue create --title "标题" --body "内容"

# 查看Issue列表
gh issue list --state open
gh issue list --state closed
gh issue list --label "FEAT-功能建议"

# 查看Issue详情
gh issue view 34
gh issue view 34 --json title,body,labels

# 编辑Issue
gh issue edit 34 --add-label "FEAT-功能建议"
gh issue edit 34 --remove-label "bug"

# 评论Issue
gh issue comment 34 --body "已完成调研，详见..."

# 关闭Issue
gh issue close 34 --reason completed
gh issue close 34 --reason "not planned"

# 重新打开Issue
gh issue reopen 34
```

### 6.2 Issue状态统计

```bash
# 按标签统计Issue数量
gh issue list --json labels --jq '[.[].labels[].name] | group_by(.) | map({label: .[0], count: length})'

# 输出示例:
# [
#   {"label": "FEAT-功能建议", "count": 13},
#   {"label": "BUG-缺陷报告", "count": 4},
#   {"label": "REF-参考", "count": 2},
#   {"label": "RES-项目资源", "count": 2},
#   {"label": "DOC-文档维护", "count": 0},
#   {"label": "HELP-求助", "count": 1},
#   {"label": "QA-提问", "count": 0}
# ]
```

### 6.3 TODO与Issue关联脚本

```python
# scripts/sync_todo_issue.py

import json

def create_todos_from_issue(issue_number, issue_title, tasks):
    """从Issue创建TODO任务列表"""
    todos = []
    for task in tasks:
        todos.append({
            "content": f"{task} (Issue #{issue_number})",
            "status": "pending",
            "activeForm": f"{task} (Issue #{issue_number})",
            "relatedIssue": f"#{issue_number}"
        })
    return todos

# 示例用法
tasks = [
    "需求分析：明确app核心功能",
    "技术选型：iOS/macOS开发框架",
    "数据接口设计：知识图谱API"
]

todos = create_todos_from_issue(34, "开发史记知识库苹果app", tasks)
print(json.dumps(todos, indent=2, ensure_ascii=False))
```

---

## 七、最佳实践

### 7.1 Issue管理规范

1. **及时分类**：新Issue创建后24小时内添加标签
2. **定期清理**：每周检查Open Issue，关闭已完成/不计划实现的Issue
3. **详细描述**：Issue描述应包含背景、现状、期望结果
4. **关联引用**：相关Issue之间用 `#数字` 互相引用

### 7.2 TODO管理规范

1. **粒度适中**：单个TODO应在1-4小时内完成
2. **状态同步**：TODO状态变更后立即更新
3. **单一in_progress**：同一时间只有1个TODO处于in_progress状态
4. **完成即标记**：完成TODO后立即标记为completed，不批量更新

### 7.3 联动规范

1. **创建TODO时关联Issue**：在TODO的content或relatedIssue字段注明Issue编号
2. **关闭Issue时检查TODO**：确保所有相关TODO已completed
3. **更新Issue时同步TODO**：Issue需求变更时，同步调整TODO任务

---

## 八、常见问题

### Q1: Issue何时关闭？

**A**: 满足以下任一条件即可关闭：

- REF类：已整理到参考文献库
- RES类：已评估并下载/归档
- FEAT类：功能已开发完成并测试通过
- BUG类：问题已修复并验证

### Q2: 一个Issue对应多少个TODO？

**A**: 取决于复杂度：

- 简单任务（标注错误修复）：1个TODO
- 中等任务（拼音注释功能）：2-3个TODO
- 复杂任务（苹果app开发）：5+个TODO，建议分阶段拆分

### Q3: TODO完成了但Issue未关闭？

**A**: 检查以下情况：

- 是否有遗漏的TODO任务？
- 功能是否经过验证？
- 是否需要文档更新？
- 确认无遗漏后，关闭Issue并添加总结评论

---

## 九、与父SKILL的关系

本SKILL（10a TODO和Issue管理）是 **SKILL_10 项目管理** 的子技能：

```
SKILL_10 项目管理
    ├─ 项目规划
    ├─ 团队协作
    ├─ 质量控制
    └─ ↓ 衍生子技能
       SKILL_10a TODO和Issue管理
           ├─ Issue分类体系
           ├─ Issue生命周期
           ├─ TODO任务对应
           └─ 批量管理脚本
```

---

## 十、参考资源

- GitHub CLI文档: https://cli.github.com/manual/gh_issue
- GitHub Issues最佳实践: https://docs.github.com/en/issues/tracking-your-work-with-issues
- 本项目Issue模板: `.github/ISSUE_TEMPLATE/` (待创建)

---

## 结语

**Issue是需求的入口，TODO是执行的抓手。** 通过系统化的分类管理和联动机制，将社区反馈、功能需求、缺陷报告有序转化为可执行的任务，确保项目持续健康发展。

每个Issue都应有明确归宿，每个TODO都应有清晰来源。
