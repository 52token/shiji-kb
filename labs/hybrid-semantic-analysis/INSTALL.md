# 安装说明

## 快速安装(推荐LTP)

如果你的显存有限或想快速开始,推荐使用LTP(几乎不占显存):

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装基础依赖
pip install pyyaml ltp anthropic -i https://pypi.tuna.tsinghua.edu.cn/simple

# 配置API key
export ANTHROPIC_API_KEY="your-key"

# 运行实验
python run_experiments.py --methods a b c
```

## 完整安装(包含Qwen小模型)

如果你有8GB显存并想测试小模型:

### 1. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装PyTorch和Transformers

**注意**: 这一步会下载约4GB的包,需要较长时间

```bash
# 使用清华源加速
pip install torch transformers sentencepiece accelerate -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 安装其他依赖

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 下载Qwen模型(可选)

**方式1**: 自动下载(首次运行时会从HuggingFace下载)

```bash
python methods/method_a_qwen.py
```

**方式2**: 手动下载到本地

```bash
# 安装HuggingFace CLI
pip install huggingface-hub

# 下载模型(约15GB)
huggingface-cli download Qwen/Qwen2.5-7B-Instruct --local-dir models/qwen2.5-7b
```

然后修改 `config.yaml`:

```yaml
local_model:
  type: "qwen"
  model_path: "models/qwen2.5-7b"
```

## 验证安装

### 测试LTP

```bash
source venv/bin/activate
python methods/method_a_local.py
```

### 测试Qwen(如已安装)

```bash
source venv/bin/activate
python methods/method_a_qwen.py
```

### 测试完整流程

```bash
source venv/bin/activate
python run_experiments.py
```

## 常见问题

### Q1: pip install torch 下载太慢

使用清华镜像源:

```bash
pip install torch -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: CUDA out of memory

降低batch_size或使用CPU:

```yaml
local_model:
  device: "cpu"
```

### Q3: 虚拟环境激活失败

确保已安装python3-venv:

```bash
sudo apt install python3-venv python3-full
```

### Q4: HuggingFace下载模型失败

设置镜像站点:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

## 显存使用参考

| 方案 | 显存占用 | 推荐配置 |
|------|----------|----------|
| LTP | <100MB | 任意 |
| Qwen2.5-7B (FP16) | 4-5GB | 8GB+ |
| Qwen2.5-7B (INT8) | 2-3GB | 6GB+ |
| GLM-4-9B (FP16) | 6-7GB | 8GB+ |

## 下一步

查看 [QUICKSTART.md](QUICKSTART.md) 了解如何运行实验。
