#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载 Qwen2.5-7B-Instruct 模型
使用 HuggingFace Hub 下载模型文件到本地缓存
"""

import os
import sys
from pathlib import Path

def download_qwen_model():
    """下载 Qwen2.5-7B-Instruct 模型"""

    print("=" * 80)
    print("开始下载 Qwen2.5-7B-Instruct 模型")
    print("=" * 80)
    print()

    # 检查是否需要代理
    hf_endpoint = os.environ.get('HF_ENDPOINT', 'https://huggingface.co')
    print(f"HuggingFace Endpoint: {hf_endpoint}")

    # 设置国内镜像 (可选)
    # os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch

        model_name = "Qwen/Qwen2.5-7B-Instruct"
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"

        print(f"\n模型: {model_name}")
        print(f"缓存目录: {cache_dir}")
        print(f"预计大小: ~15GB")
        print(f"设备: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
        print()

        # 1. 下载 tokenizer (小文件,几MB)
        print("步骤 1/2: 下载 Tokenizer...")
        print("-" * 80)
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        print("✓ Tokenizer 下载完成")
        print()

        # 2. 下载模型 (大文件,~15GB)
        print("步骤 2/2: 下载模型权重 (~15GB, 预计10-30分钟)...")
        print("-" * 80)
        print("提示: 可以按 Ctrl+C 中断,下次会断点续传")
        print()

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,  # 使用FP16节省显存
            device_map="auto" if torch.cuda.is_available() else "cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True  # 减少CPU内存占用
        )

        print()
        print("✓ 模型下载完成!")
        print()

        # 显示模型信息
        print("=" * 80)
        print("模型信息")
        print("=" * 80)
        print(f"模型名称: {model_name}")
        print(f"参数量: 7B")
        print(f"精度: FP16")

        # 计算实际占用的显存
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            print(f"显存占用: {allocated:.2f}GB (已分配) / {reserved:.2f}GB (已保留)")

        # 查看缓存大小
        import subprocess
        result = subprocess.run(
            ["du", "-sh", str(cache_dir)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            cache_size = result.stdout.split()[0]
            print(f"缓存总大小: {cache_size}")

        print()
        print("=" * 80)
        print("下载成功! 现在可以运行实际标注测试:")
        print("  python methods/method_a_qwen.py")
        print("=" * 80)

        return True

    except KeyboardInterrupt:
        print("\n\n下载已中断。下次运行会自动断点续传。")
        return False
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 如果在国内,可以设置镜像:")
        print("   export HF_ENDPOINT=https://hf-mirror.com")
        print("3. 确保有足够的磁盘空间 (至少20GB)")
        return False

if __name__ == "__main__":
    # 检查依赖
    try:
        import transformers
        import torch
        print(f"PyTorch 版本: {torch.__version__}")
        print(f"Transformers 版本: {transformers.__version__}")
        print(f"CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA 版本: {torch.version.cuda}")
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"GPU 显存: {total_memory:.2f}GB")
        print()
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请先运行: pip install torch transformers")
        sys.exit(1)

    success = download_qwen_model()
    sys.exit(0 if success else 1)
