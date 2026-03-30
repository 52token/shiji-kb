# SKILL_01d 正音与拼音标注

**技能类别**: 文本处理与显示
**技能等级**: 中级
**适用场景**: 为史记文本添加拼音注释，处理特殊读音
**创建日期**: 2026-03-31
**最后更新**: 2026-03-31

## 技能概述

本SKILL描述如何为《史记》文本添加准确的拼音注释，特别是处理古代人名、地名、族群称号等特殊读音词汇。通过Ruby标注技术实现拼音与汉字的精确对齐，并维护特殊读音词表确保读音准确性。

## 相关文档

### 规范文档 (Specs)

| 文档 | 路径 | 说明 |
|------|------|------|
| 拼音注释功能规范 | `doc/spec/拼音注释功能规范.md` | 拼音功能的完整技术规范 |
| 特殊读音词表维护说明 | `doc/spec/特殊读音词表维护说明.md` | 特殊读音词表的维护指南 |
| 正义版词表说明 | `doc/spec/特殊读音词表_正义版_说明.md` | 从正义提取词表的说明文档 |
| 正义提取结果 | `doc/spec/特殊读音注释提取结果.md` | 完整提取结果（694行） |

### 数据文件 (Data)

| 文件 | 路径 | 说明 |
|------|------|------|
| 特殊读音词表 | `docs/data/special-pronunciation.json` | 合并词表（v2.0）：52词条，含人工整理+正义提取 |

### 代码文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 拼音注释脚本 | `docs/js/heading-pinyin.js` | 前端拼音标注核心逻辑 |
| 设置面板脚本 | `docs/js/settings-panel.js` | 拼音开关控制 |
| 拼音样式 | `docs/css/shiji-styles.css` (行245-298) | Ruby标注CSS样式 |

### HTML生成

| 文件 | 路径 | 说明 |
|------|------|------|
| HTML渲染器 | `render_shiji_html.py` | 集成拼音脚本引用 |

## 核心功能

### 1. 标准拼音注释

为所有汉字自动添加带声调的拼音注释，使用HTML5标准的 `<ruby>` 标注：

```html
<ruby>
  <span class="hanzi">黄</span>
  <rt class="pinyin-rt">huáng</rt>
</ruby>
```

**覆盖范围**:
- 标题（h1, h2, h3）
- 正文段落（p）
- 引用块（blockquote）
- 列表项（li）

### 2. 特殊读音处理

自动识别并应用特殊读音词表中定义的读音。

**处理流程**:
1. 加载 `docs/data/special-pronunciation.json`
2. 按词长降序排序（优先匹配长词）
3. 从左到右扫描文本
4. 完全匹配时应用特殊读音
5. 未匹配时使用标准读音（pinyin-pro库）

**匹配示例**:
```
原文: "冒顿单于"
标准读音: mào dùn dān yú (错误)
特殊读音: mò dú chán yú (正确✓)
```

### 3. 用户控制

通过设置面板控制拼音显示：
- 默认开启拼音注释
- 可随时关闭/开启
- 状态持久化到 localStorage

## 使用步骤

### 步骤1: 生成带拼音的HTML

```bash
# 生成单个章节
python render_shiji_html.py chapter_md/001_五帝本纪.tagged.md docs/chapters/001_五帝本纪.html

# 批量生成所有章节
python generate_all_chapters.py
```

生成的HTML会自动包含：
- 拼音脚本引用 (`heading-pinyin.js`)
- 拼音样式引用 (`shiji-styles.css`)
- 拼音开关选项（设置面板）

### 步骤2: 查看拼音效果

在浏览器中打开生成的HTML文件：
- 每个汉字上方显示拼音
- 拼音与汉字精确对齐
- 特殊读音词自动应用正确读音

### 步骤3: 控制拼音显示

点击页面右上角设置按钮（⚙️）：
- 勾选"拼音注释"显示拼音
- 取消勾选隐藏拼音
- 设置自动保存

## 从《史记正义》中提取特殊读音

### 方法论概述

《史记正义》（唐代张守节撰）是提取特殊读音的最权威来源。正义中使用中古反切和直音法标注了大量古今读音差异的字词。

### 提取流程

#### 1. 识别读音注释模式

《史记正义》中有4种常见读音标注模式：

**模式1: 反切注音**
```
格式: "某音甲乙反"
示例: "阏，于达反" → yān
      "与音预" → yǔ
      "亢音刚，父音甫" → gāng fǔ
```

**模式2: 直接注音**
```
格式: "某音某"
示例: "音焉与" → yān yǔ
      "音潮" → cháo
      "令音铃" → líng
```

**模式3: 通假注音**
```
格式: "某读曰某" 或 "某读为某"
示例: "驯读曰训"
      "施读为移"
```

**模式4: 类比注音**
```
格式: "某如某"
示例: "朝音潮（如'潮汐'之潮）"
```

#### 2. 搜索策略

在《史记集解三家注索隐正义》中搜索：

```bash
# 方法1: 直接搜索地名+音注
grep -E "地名.*音|音.*地名" archive/史记集解三家注索隐正义.txt

# 方法2: 搜索"正义"段落中的读音标注
grep -A 3 "正义.*音" archive/史记集解三家注索隐正义.txt

# 方法3: 搜索反切模式
grep -E "音.{1,3}反|读曰|读为" archive/史记集解三家注索隐正义.txt
```

#### 3. 反切转现代拼音

**反切原理**: 取上字声母+下字韵母

常见反切示例：
```
于达反 → yān/è (取"于"的y声母+"达"的韵母)
巨用反 → gòng (取"巨"的g声母+"用"的韵母)
丘袁反 → quān (取"丘"的q声母+"袁"的韵母)
况于反 → xū (取"况"的k/x声母+"于"的韵母)
```

**注意事项**:
- 中古音与现代音有差异，需对照现代读音确认
- 同一反切可能对应多个现代音（如"于达反"可能是è或yān）
- 优先参考《史记正义》给出的直音（如"音焉与"）

#### 4. 验证在史记中出现

```bash
# 验证词条是否在史记原文中出现
grep "词条" archive/史记.简体.txt

# 统计出现次数
grep -c "词条" archive/史记.简体.txt
```

**重要原则**: 只收录在《史记》原文中确实出现的词条。

#### 5. 分类整理

按以下类别整理：
- **地名**: 阏与(yān yǔ)、亢父(gāng fǔ)、卷县(quān xiàn)
- **官职**: 仆射(pú yè)、大行(dà háng)
- **人名**: 樗里(chū lǐ)、盱眙(xū yí)
- **多音字**: 王(wàng动词)、将(jiàng名词)、相(xiàng名词)

### 提取工具

**脚本**: `scripts/extract_special_pronunciations_v2.py`

```bash
# 运行提取脚本
python3 scripts/extract_special_pronunciations_v2.py

# 输出: doc/spec/特殊读音注释提取结果.md
```

**转换与合并脚本**: `scripts/convert_pronunciation_to_json.py`

```bash
# 将提取结果转换为JSON并合并到主词表
python3 scripts/convert_pronunciation_to_json.py

# 合并后统一保存到: docs/data/special-pronunciation.json
```

**注意**: 词表已合并为单一文件（v2.0），来自正义的词条在note中标注`[史记正义]`前缀。

### 质量检查清单

添加新词条前必须检查：

- [ ] 在《史记正义》中有明确注音
- [ ] 在《史记》原文中确实出现
- [ ] 反切转换正确（对照多个来源）
- [ ] 与现代标准读音有显著差异（有实用价值）
- [ ] JSON格式正确（拼音数组长度=文字长度）
- [ ] 已在浏览器中验证显示效果

### 参考文档

- **完整提取结果**: `doc/spec/特殊读音注释提取结果.md` (694行)
- **合并词表**: `docs/data/special-pronunciation.json` (v2.0, 52词条)
- **正义版说明**: `doc/spec/特殊读音词表_正义版_说明.md`

---

## 添加特殊读音

当发现史记中的特殊读音词未被正确标注时：

### 步骤1: 确认读音

查阅权威资料确认正确读音（优先级从高到低）：
1. **《史记正义》**（最权威）
2. **《史记索隐》**
3. **《史记集解》**
4. 《汉语大字典》
5. 学术论文

### 步骤2: 编辑词表

编辑 `docs/data/special-pronunciation.json`：

```json
{
  "text": "冒顿",
  "pinyin": ["mò", "dú"],
  "context": "匈奴单于名",
  "note": "冒顿单于，匈奴历史上著名单于，'冒'读mò，'顿'读dú"
}
```

**必填字段**:
- `text`: 词汇原文
- `pinyin`: 每个字的拼音数组（带声调）
- `context`: 词汇类别
- `note`: 详细注释

### 步骤3: 验证读音

```bash
# 重新生成包含该词的HTML
python render_shiji_html.py chapter_md/110_匈奴列传.tagged.md docs/chapters/110_匈奴列传.html

# 在浏览器中打开，验证读音正确
```

### 步骤4: 更新文档

更新 `lastUpdated` 字段：
```json
{
  "lastUpdated": "2026-03-31"
}
```

## 常见特殊读音类别

### 人名

| 原文 | 标准读音（错） | 特殊读音（正确） | 说明 |
|------|--------------|-----------------|------|
| 冒顿 | mào dùn | mò dú | 匈奴单于名 |
| 句践 | jù jiàn | gōu jiǎn | 越王名 |
| 夫差 | fū chà | fú chāi | 吴王名 |
| 员 | yuán | yùn | 伍子胥名 |

### 地名

| 原文 | 标准读音（错） | 特殊读音（正确） | 说明 |
|------|--------------|-----------------|------|
| 会稽 | huì jī | kuài jī | 古郡名 |
| 番禺 | fān yú | pān yú | 古县名 |
| 华山 | huá shān | huà shān | 五岳之一 |
| 朝歌 | cháo gē | zhāo gē | 古都名 |

### 称号

| 原文 | 标准读音（错） | 特殊读音（正确） | 说明 |
|------|--------------|-----------------|------|
| 单于 | dān yú | chán yú | 匈奴君主称号 |
| 阏氏 | è shì | yān zhī | 匈奴皇后称号 |
| 可汗 | kě hàn | kè hán | 突厥君主称号 |

### 姓氏

| 原文 | 标准读音（错） | 特殊读音（正确） | 说明 |
|------|--------------|-----------------|------|
| 华 | huá | huà | 华姓 |
| 解 | jiě | xiè | 解姓 |
| 区 | qū | ōu | 区姓 |
| 查 | chá | zhā | 查姓 |
| 仇 | chóu | qiú | 仇姓 |
| 种 | zhǒng | chóng | 种姓 |

## 技术细节

### Ruby标注结构

```html
<!-- 普通汉字 -->
<ruby>
  <span class="hanzi">黄</span>
  <rt class="pinyin-rt">huáng</rt>
</ruby>

<!-- 特殊读音词 -->
<ruby>
  <span class="hanzi">冒</span>
  <rt class="pinyin-rt pinyin-special" title="冒顿单于特殊读音">mò</rt>
</ruby>
<ruby>
  <span class="hanzi">顿</span>
  <rt class="pinyin-rt pinyin-special" title="冒顿单于特殊读音">dú</rt>
</ruby>
```

### CSS样式控制

```css
/* 拼音文本样式 */
rt.pinyin-rt {
    font-size: 0.5em;
    color: #7a6e62;
    letter-spacing: 0.03em;
    padding: 0 0.08em;
}

/* 特殊读音标识 */
rt.pinyin-rt.pinyin-special {
    cursor: help;  /* 鼠标悬停显示帮助提示 */
}

/* 拼音隐藏 */
body.pinyin-off rt.pinyin-rt {
    display: none;
}
```

### JavaScript匹配算法

```javascript
// 特殊读音匹配（从长到短）
function matchSpecialPronunciation(text, startIndex) {
  // 遍历词表（已按长度降序排序）
  for (let entry of specialPronunciations) {
    const substr = text.substring(startIndex, startIndex + entry.text.length);
    if (substr === entry.text) {
      return {
        text: entry.text,
        pinyin: entry.pinyin,
        length: entry.text.length,
        note: entry.note
      };
    }
  }
  return null;
}
```

## 性能优化

### 1. 异步加载

```javascript
// 词表和拼音库并行加载
await loadSpecialPronunciations();
const pinyinFn = await import('pinyin-pro');
```

### 2. 分帧处理

使用 `requestIdleCallback` 避免长页面卡顿：

```javascript
function processChunk(deadline) {
  while (index < elements.length) {
    if (deadline.timeRemaining() < 8) break;
    addPinyinToElement(elements[index++], pinyinFn);
  }
  if (index < elements.length) {
    requestIdleCallback(processChunk);
  }
}
```

### 3. 缓存机制

```javascript
// 多音字判断缓存
const polyCache = new Map();
function isPolyphonicCached(ch) {
  if (polyCache.has(ch)) return polyCache.get(ch);
  const result = checkPolyphonic(ch);
  polyCache.set(ch, result);
  return result;
}
```

## 故障排除

### 问题1: 拼音不显示

**检查项**:
1. 浏览器控制台是否有错误
2. 网络是否能访问CDN（pinyin-pro）
3. 拼音开关是否被关闭

### 问题2: 特殊读音不生效

**检查项**:
1. JSON格式是否正确（使用验证工具）
2. `pinyin`数组长度是否等于`text`长度
3. 浏览器控制台是否有加载失败警告

### 问题3: 拼音间距太紧/太松

**调整方案**:
编辑 `docs/css/shiji-styles.css`：

```css
ruby { margin: 0 0.03em; }           /* Ruby元素间距 */
rt.pinyin-rt {
    letter-spacing: 0.03em;          /* 字母间距 */
    padding: 0 0.08em;               /* 拼音padding */
}
```

## 测试检查清单

- [ ] 标题拼音显示正确
- [ ] 正文段落拼音显示正确
- [ ] 引用块拼音显示正确
- [ ] 列表项拼音显示正确
- [ ] 特殊读音词自动应用（如"冒顿单于"）
- [ ] 拼音开关功能正常
- [ ] 关闭拼音后行高恢复正常
- [ ] localStorage持久化正常
- [ ] 鼠标悬停特殊读音显示提示
- [ ] 不同浏览器显示一致

## 维护建议

### 定期任务

1. **补充特殊读音词表**（月度）
   - 收集用户反馈的读音问题
   - 查阅学术资料确认读音
   - 批量添加到词表

2. **验证词表准确性**（季度）
   - 与权威版本对照
   - 更新过时或错误的读音
   - 补充注释说明

3. **性能监控**（随机）
   - 监测长页面加载时间
   - 优化分帧处理阈值
   - 更新CDN镜像列表

### 改进方向

- [ ] 支持多音字自动选择上下文读音
- [ ] 添加方言读音支持
- [ ] 提供拼音导出功能（用于朗读）
- [ ] 集成语音合成（TTS）功能

## 相关Issue

- #25: 希望增加拼音注释，方便阅读

## 参考资料

### 技术文档

- [HTML Ruby标注规范](https://www.w3.org/TR/html52/textlevel-semantics.html#the-ruby-element)
- [pinyin-pro库文档](https://github.com/zh-lx/pinyin-pro)
- [CSS Ruby Layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_ruby_layout)

### 学术资源

- 《史记》三家注（裴骃、司马贞、张守节）
- 《汉语大字典》
- 《古音韵表》
- 中华书局版《史记》注释

## 更新日志

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-03-31 | 2.0 | 合并词表v2.0：人工整理+正义提取，统一为单一JSON文件（52词条） |
| 2026-03-31 | 1.1 | 新增：从《史记正义》提取特殊读音的方法论 |
| 2026-03-31 | 1.0 | 初始版本：Ruby标注、特殊读音词表 |

---

**技能标签**: #拼音 #Ruby标注 #特殊读音 #前端 #可读性
**维护者**: Claude
**审核状态**: ✓ 已完成
