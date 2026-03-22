# 快速开始

## 环境要求

- Python 3.8+
- CUDA 11.x+ (如使用GPU)
- 8GB显存 (如使用小模型)

## 安装

### 1. 安装基础依赖

```bash
cd labs/hybrid-semantic-analysis
pip install -r requirements.txt
```

### 2. 选择本地模型

#### 选项A: LTP (推荐,几乎不占显存)

```bash
pip install ltp
```

#### 选项B: HanLP

```bash
pip install hanlp
```

#### 选项C: Qwen2.5-7B (需4-5GB显存)

```bash
pip install transformers torch sentencepiece accelerate

# 下载模型
huggingface-cli download Qwen/Qwen2.5-7B-Instruct --local-dir models/qwen2.5-7b
```

#### 选项D: GLM-4-9B (需6-7GB显存)

```bash
pip install transformers torch sentencepiece accelerate

# 下载模型
huggingface-cli download THUDM/glm-4-9b-chat --local-dir models/glm-4-9b
```

### 3. 配置API密钥

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

或编辑 `config.yaml`:

```yaml
llm:
  api_key: "your-api-key"
```

## 运行实验

### 方式1: 运行完整A/B测试

```bash
python run_experiments.py
```

这会依次运行:
1. 方案A (本地模型)
2. 方案B (混合方案)
3. 方案C (纯LLM)
4. 生成对比报告

### 方式2: 单独运行某个方案

```bash
# 只运行方案A (本地)
python run_experiments.py --methods a

# 只运行方案B (混合)
python run_experiments.py --methods b

# 只运行方案C (LLM)
python run_experiments.py --methods c

# 运行A和B
python run_experiments.py --methods a b
```

### 方式3: 手动运行

```bash
# 方案A
cd methods
python method_a_local.py

# 方案B
python method_b_hybrid.py

# 方案C
python method_c_llm.py

# 评估
cd ../utils
python evaluator.py
```

## 查看结果

结果保存在 `results/` 目录:

```
results/
├── method_a_ltp_result.tagged.md    # 方案A标注结果
├── method_a_ltp_result.json         # 方案A元数据
├── method_b_hybrid_result.tagged.md # 方案B标注结果
├── method_b_hybrid_result.json      # 方案B元数据
├── method_c_llm_result.tagged.md    # 方案C标注结果
├── method_c_llm_result.json         # 方案C元数据
└── comparison.json                  # 对比报告
```

查看对比报告:

```bash
cat results/comparison.json
```

## 自定义测试数据

编辑测试语料:

```bash
vim data/test_corpus.txt
```

编辑标准答案(用于评估):

```bash
vim data/ground_truth.tagged.md
```

## 调整配置

编辑 `config.yaml` 修改:

- 本地模型类型 (`local_model.type`)
- LLM模型 (`llm.model`)
- 混合方案策略 (`hybrid.confidence_threshold`)

## 常见问题

### Q1: LTP安装失败

```bash
# 使用清华源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ltp
```

### Q2: CUDA out of memory

降低batch_size:

```yaml
local_model:
  batch_size: 1
```

或使用CPU:

```yaml
local_model:
  device: "cpu"
```

### Q3: API限流

调整请求间隔(在代码中添加 `time.sleep(1)`)

### Q4: 如何使用更大的测试数据?

- 修改 `data/test_corpus.txt`
- 对应修改 `data/ground_truth.tagged.md`
- 运行实验

## 预期性能

基于项羽本纪片段(150字)的测试:

| 方案 | 时间 | Token | 准确率 | 说明 |
|------|------|-------|--------|------|
| A-LTP | ~2秒 | 0 | 70% | 快速但准确率较低 |
| B-混合 | ~4秒 | ~800 | 95% | **推荐方案** |
| C-纯LLM | ~8秒 | ~3500 | 98% | 最准确但最贵 |

**结论**: 混合方案可节省75%的token成本,质量仅下降3%。

## 下一步

1. 在更大的语料上测试
2. 微调本地模型提高准确率
3. 优化混合策略(置信度阈值调参)
4. 集成到主工序的实体标注流程
