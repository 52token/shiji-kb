# 混合语义分析实验

## 实验目标

对比三种语义分析方案的成本和效果:

- **方案A (纯本地)**: 使用本地NLP工具(依存文法/小模型)完成语义标注
- **方案B (混合)**: 本地模型粗标注 + LLM精炼修正
- **方案C (纯LLM)**: 直接使用大模型完成语义标注(对照组)

## 评估指标

- **时间成本**: 总耗时(秒)
- **Token成本**: API调用总token数
- **质量评估**: 标注准确率、实体召回率、关系准确性
- **显存占用**: 本地模型推理峰值显存

## 技术方案

### 方案A: 纯本地NLP

**工具选择(8G显存)**:

1. **依存文法分析** (推荐,几乎不占显存)
   - LTP 4.x (哈工大)
   - HanLP 2.x

2. **小规模语言模型** (4-7GB显存)
   - Qwen2.5-7B-Instruct (阿里)
   - GLM-4-9B-Chat (智谱)

**流程**:
```
原文 → 分词/词性标注 → 依存句法分析 → 规则提取实体 → 关系抽取 → 输出标注
```

### 方案B: 混合方案

**流程**:
```
原文 → 本地模型粗标注 → LLM review修正 → 输出标注
```

**优势**:
- 本地模型处理90%常见实体(人名/地名/官职)
- LLM只处理疑难案例和关系推理
- 大幅降低token消耗

### 方案C: 纯LLM (对照组)

**流程**:
```
原文 → Claude API (完整标注) → 输出标注
```

## 测试数据

从已标注章节选取典型片段(100-500字):

- 人物密集型: 如《项羽本纪》战争片段
- 地名密集型: 如《河渠书》地理描述
- 关系复杂型: 如《陈涉世家》起义叙事

## 目录结构

```
labs/hybrid-semantic-analysis/
├── README.md              # 本文件
├── MODEL_STORAGE.md       # 模型文件存储位置说明
├── requirements.txt       # Python依赖
├── config.yaml            # 配置文件(模型路径/API key)
├── download_qwen.py       # Qwen2.5-7B 下载脚本
├── data/
│   ├── test_corpus.txt    # 测试语料
│   └── ground_truth.tagged.md  # 人工标注的参考答案
├── methods/
│   ├── method_a_local.py  # 方案A: 纯本地
│   ├── method_b_hybrid.py # 方案B: 混合
│   └── method_c_llm.py    # 方案C: 纯LLM
├── utils/
│   ├── evaluator.py       # 评估工具
│   └── tokenizer.py       # Token计数工具
├── results/
│   ├── experiment_summary.md      # 实验总结报告
│   ├── ltp_experiment_report.md   # LTP详细分析
│   ├── method_a_ltp_result.tagged.md
│   ├── method_a_qwen_result.tagged.md
│   ├── method_b_result.tagged.md
│   ├── method_c_result.tagged.md
│   └── comparison.json    # 对比结果
├── models/                # 本地模型目录 (已在.gitignore中)
└── notebooks/
    └── analysis.ipynb     # 结果分析notebook
```

## 快速开始

### 1. 安装依赖

```bash
cd labs/hybrid-semantic-analysis
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 下载模型

**下载 Qwen2.5-7B** (~15GB, 10-30分钟):
```bash
python download_qwen.py
```

**查看模型存储位置**: 参见 [MODEL_STORAGE.md](MODEL_STORAGE.md)
- 默认位置: `~/.cache/huggingface/hub/`
- 支持断点续传
- 不会提交到 git (已配置 .gitignore)

### 3. 配置

编辑 `config.yaml`:

```yaml
# 本地模型配置
local_model:
  type: "ltp"  # 可选: ltp / hanlp / qwen / glm
  model_path: "/path/to/model"  # 仅小模型需要
  device: "cuda"  # cuda / cpu

# LLM配置
llm:
  provider: "anthropic"  # anthropic / openai
  api_key: "${ANTHROPIC_API_KEY}"
  model: "claude-3-5-sonnet-20241022"

# 评估配置
evaluation:
  ground_truth: "data/ground_truth.tagged.md"
```

### 4. 运行实验

```bash
# 方案A: 纯本地
python methods/method_a_local.py

# 方案B: 混合
python methods/method_b_hybrid.py

# 方案C: 纯LLM
python methods/method_c_llm.py

# 对比结果
python utils/evaluator.py
```

## 预期结果

| 方案 | 时间(秒) | Token消耗 | 准确率 | 召回率 | 显存(GB) |
|------|---------|----------|--------|--------|----------|
| A-依存文法 | ~2 | 0 | 60-70% | 80-90% | <1 |
| A-Qwen7B | ~5 | 0 | 75-85% | 85-95% | 5 |
| B-混合(LTP+LLM) | ~3 | 500-1000 | 90-95% | 95-98% | <1 |
| B-混合(Qwen+LLM) | ~6 | 300-800 | 92-97% | 96-99% | 5 |
| C-纯LLM | ~10 | 3000-5000 | 95-99% | 98-100% | 0 |

**结论预期**:
- 方案B(混合)可节省70-80% token成本
- 质量仅比纯LLM低2-5个百分点
- 适合大规模批量标注

## 下一步

- [ ] 实现三种方案的代码
- [ ] 准备测试语料和ground truth
- [ ] 运行A/B测试
- [ ] 分析结果并撰写报告
- [ ] 将最优方案集成到主工序
