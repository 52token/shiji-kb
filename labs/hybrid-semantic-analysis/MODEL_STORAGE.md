# 模型文件存储位置说明

本文档说明各类模型文件的存储位置和管理方法。

---

## 一、模型文件保存位置

### 1.1 HuggingFace 模型缓存 (推荐)

**默认位置**: `~/.cache/huggingface/hub/`

**说明**:
- 所有通过 `transformers` 库下载的模型默认保存在此
- 支持断点续传
- 多个项目可共享同一模型缓存
- Git 自动忽略 (不在项目目录内)

**示例路径**:
```
~/.cache/huggingface/hub/
├── models--Qwen--Qwen2.5-7B-Instruct/
│   ├── blobs/                        # 实际文件存储 (去重)
│   ├── refs/                         # 引用
│   └── snapshots/                    # 快照
│       └── [commit_hash]/
│           ├── config.json
│           ├── generation_config.json
│           ├── model-00001-of-00004.safetensors  (~3.8GB)
│           ├── model-00002-of-00004.safetensors  (~3.8GB)
│           ├── model-00003-of-00004.safetensors  (~3.8GB)
│           ├── model-00004-of-00004.safetensors  (~3.5GB)
│           ├── tokenizer.json
│           ├── tokenizer_config.json
│           └── vocab.json
├── models--THUDM--glm-4-9b-chat/     # (如果下载了GLM)
└── models--dslim--bert-base-NER/     # (其他模型)
```

**模型大小**:
- **Qwen2.5-7B-Instruct**: ~15GB
- **GLM-4-9B-Chat**: ~18GB
- **LTP-base**: ~500MB
- **BERT-base-NER**: ~400MB

### 1.2 LTP 模型缓存

**默认位置**: `~/.cache/ltp/`

**说明**:
- LTP 依存文法模型独立缓存
- 首次运行自动下载
- 大小约 500MB

**示例路径**:
```
~/.cache/ltp/
├── ltp_base.model
└── ltp_base_v2.model
```

### 1.3 项目本地目录 (可选)

**位置**: `labs/hybrid-semantic-analysis/models/`

**说明**:
- 已在 `.gitignore` 中排除
- 适合手动下载或自定义模型
- 不会提交到 git 仓库

**配置方法**:
```python
from transformers import AutoModel

# 下载到项目目录
model = AutoModel.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct",
    cache_dir="./models"  # 指定项目本地目录
)
```

---

## 二、查看和管理模型

### 2.1 查看已下载的模型

```bash
# 查看 HuggingFace 缓存
ls -lh ~/.cache/huggingface/hub/

# 查看缓存总大小
du -sh ~/.cache/huggingface/hub/

# 查看特定模型
ls -lh ~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct/

# 查看 LTP 缓存
ls -lh ~/.cache/ltp/
```

### 2.2 清理模型缓存

**删除特定模型**:
```bash
# 删除 Qwen2.5-7B
rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct

# 删除 GLM-4
rm -rf ~/.cache/huggingface/hub/models--THUDM--glm-4-9b-chat
```

**清空所有缓存** (谨慎使用!):
```bash
# 清空 HuggingFace 缓存
rm -rf ~/.cache/huggingface/hub/*

# 清空 LTP 缓存
rm -rf ~/.cache/ltp/*
```

**使用 huggingface-cli 管理** (推荐):
```bash
# 安装 CLI 工具
pip install huggingface_hub

# 查看缓存信息
huggingface-cli scan-cache

# 删除未使用的模型
huggingface-cli delete-cache
```

### 2.3 磁盘空间监控

```bash
# 查看各目录大小
du -h ~/.cache/huggingface/hub/ | sort -h | tail -20

# 查看磁盘可用空间
df -h ~
```

---

## 三、模型下载配置

### 3.1 设置 HuggingFace Token (可选)

**作用**: 提高下载速度,访问私有模型

```bash
# 设置环境变量
export HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxx"

# 或在代码中
from huggingface_hub import login
login(token="hf_xxxxxxxxxxxxxxxxxxxxx")
```

**获取 Token**: https://huggingface.co/settings/tokens

### 3.2 使用国内镜像 (可选)

**HuggingFace 镜像站**:
```bash
# 设置镜像 (临时)
export HF_ENDPOINT=https://hf-mirror.com

# 或在代码中
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
```

**常用镜像**:
- 官方: `https://huggingface.co` (默认)
- 国内镜像: `https://hf-mirror.com`

### 3.3 断点续传

HuggingFace Hub 自动支持断点续传:
- 下载中断后,重新运行会继续下载
- 不会重复下载已有的文件
- 使用 HTTP Range 请求

---

## 四、.gitignore 配置

确保大模型文件不会被提交到 git:

```gitignore
# 模型文件 (不提交到 git)
models/
*.bin
*.safetensors
*.pt
*.pth
*.onnx
*.msgpack
*.h5

# HuggingFace 缓存
.cache/
hub/

# LTP 缓存
ltp_data/

# 虚拟环境
venv/
env/
```

**验证**:
```bash
# 查看 git 忽略的文件
git status --ignored

# 确保模型文件不在 git 追踪中
git ls-files | grep -E "\.(bin|safetensors|pt|pth)$"
# 应该没有输出
```

---

## 五、常见问题

### Q1: 模型下载失败怎么办?

**解决方案**:
1. 检查网络连接
2. 使用国内镜像: `export HF_ENDPOINT=https://hf-mirror.com`
3. 设置 HF_TOKEN (如果是访问限制)
4. 确保磁盘空间充足 (至少 20GB)
5. 重新运行 (支持断点续传)

### Q2: 下载速度很慢怎么办?

**解决方案**:
1. 使用国内镜像站
2. 设置 HF_TOKEN 提高速率限制
3. 使用有线网络而非 WiFi
4. 避开高峰时段

### Q3: 如何在多个项目间共享模型?

**解决方案**:
- 使用默认缓存目录 `~/.cache/huggingface/hub/`
- 所有项目自动共享同一模型
- 不需要重复下载

### Q4: 模型占用太多磁盘空间怎么办?

**解决方案**:
```bash
# 1. 删除不常用的模型
huggingface-cli delete-cache

# 2. 只保留必要的模型
rm -rf ~/.cache/huggingface/hub/models--[不需要的模型]

# 3. 使用量化模型 (更小)
# 例如: Qwen2.5-7B-Instruct-GPTQ (4-bit 量化, ~4GB)
```

### Q5: 模型下载了但找不到?

**查找方法**:
```bash
# 搜索 safetensors 文件
find ~/.cache/huggingface -name "*.safetensors" -type f

# 搜索特定模型
find ~/.cache/huggingface -name "*Qwen*" -type d
```

---

## 六、本项目模型清单

### 6.1 已下载的模型

| 模型 | 用途 | 大小 | 位置 |
|------|------|------|------|
| Qwen2.5-7B-Instruct | 实体标注 | ~15GB | `~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct/` |
| LTP-base | 依存文法 | ~500MB | `~/.cache/ltp/` (首次运行自动下载) |
| BERT-base-NER | 命名实体识别 | ~400MB | `~/.cache/huggingface/hub/models--dslim--bert-base-NER/` |

### 6.2 可选模型

| 模型 | 用途 | 大小 | 下载命令 |
|------|------|------|----------|
| GLM-4-9B-Chat | 实体标注备选 | ~18GB | `python download_glm.py` |
| Qwen2.5-7B-GPTQ | 量化版本 | ~4GB | (需额外配置) |

### 6.3 估算总空间需求

**最小配置** (仅 LTP):
- LTP: 500MB
- **总计**: ~1GB

**推荐配置** (LTP + Qwen):
- LTP: 500MB
- Qwen2.5-7B: 15GB
- **总计**: ~16GB

**完整配置** (LTP + Qwen + GLM):
- LTP: 500MB
- Qwen2.5-7B: 15GB
- GLM-4-9B: 18GB
- **总计**: ~34GB

---

## 七、自动化脚本

### 7.1 下载脚本

**下载 Qwen2.5-7B**:
```bash
python download_qwen.py
```

**下载 GLM-4-9B** (待实现):
```bash
python download_glm.py
```

### 7.2 检查脚本

**检查已安装的模型**:
```bash
python check_models.py
```

**输出示例**:
```
✓ Qwen2.5-7B-Instruct: 已安装 (15.2GB)
✓ LTP-base: 已安装 (487MB)
✗ GLM-4-9B-Chat: 未安装
```

### 7.3 清理脚本

**清理未使用的模型**:
```bash
python cleanup_models.py --dry-run  # 预览
python cleanup_models.py --force    # 执行
```

---

## 八、参考链接

- **HuggingFace Hub**: https://huggingface.co/docs/hub/
- **HuggingFace CLI**: https://huggingface.co/docs/huggingface_hub/guides/cli
- **Qwen2.5 模型**: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct
- **LTP 文档**: https://ltp.ai/
- **国内镜像站**: https://hf-mirror.com/

---

**文档更新**: 2026-03-22
**维护者**: shiji-kb 项目组
