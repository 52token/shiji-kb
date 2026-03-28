# 出版物草稿目录

本目录包含项目相关的出版物草稿和创作实验。

## 📝 技术文章

- **[从历史书中探索知识图谱.tagged.md](从历史书中探索知识图谱.tagged.md)**: 14页PDF完整记录

## 🎨 创作实验 (2026-03-26 新增)

- **[养虾人列传_太史公版.md](养虾人列传_太史公版.md)**: AI文风实验，用太史公体风格记述现代养虾人故事
- **[故事宇宙的时间开始了.md](故事宇宙的时间开始了.md)**: 创作实践（现代版）
- **[故事宇宙的时间开始了_太史公版.md](故事宇宙的时间开始了_太史公版.md)**: 创作实践（太史公版）

---

## 使用专用渲染器

技术文章使用专用渲染器 `render_tech_article.py`，支持：

1. **技术文章特定实体**
   - 〖#术语〗 `.terminology`
   - 〖※职业〗 `.profession`  
   - 〖★方法论〗 `.methodology`
   - 〖|典籍〗 `.book`（技术文章格式）

2. **知识工程动词**
   - ⟦◆构建⟧ `.verb-construct`
   - ⟦◇处理⟧ `.verb-process`
   - ⟦◎推理⟧ `.verb-reason`
   - ⟦◈应用⟧ `.verb-apply`

3. **排版特性**
   - 句子级排版（每句一行）
   - 语义缩进（因果、递进等逻辑关系）
   - 自动添加文章日期

## 渲染命令

```bash
python render_tech_article.py resources/publications/draft/从历史书中探索知识图谱.tagged.md
```

## CSS样式

技术文章使用同目录下的 `kg-tech-article-styles.css`
