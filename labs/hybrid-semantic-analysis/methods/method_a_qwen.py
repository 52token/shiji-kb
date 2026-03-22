"""
方案A: 使用Qwen2.5-7B小模型进行标注

适合8GB显存,实际占用约4-5GB
"""

import sys
import yaml
import logging
from pathlib import Path
from typing import List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    Entity,
    AnnotationResult,
    Timer,
    parse_tagged_text,
)


class QwenAnnotator:
    """基于Qwen2.5-7B的标注器"""

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        """加载Qwen模型"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch

            model_path = self.config.get("model_path")
            if not model_path:
                # 默认使用HuggingFace Hub
                model_path = "Qwen/Qwen2.5-7B-Instruct"

            device = self.config.get("device", "cuda")

            self.logger.info(f"加载Qwen模型: {model_path}")

            # 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True
            )

            # 加载模型
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                trust_remote_code=True
            )

            if device == "cpu":
                self.model = self.model.to(device)

            self.model.eval()

            self.logger.info(f"Qwen模型加载成功 (device={device})")

        except Exception as e:
            self.logger.error(f"Qwen模型加载失败: {e}")
            raise

    def annotate(self, text: str) -> AnnotationResult:
        """
        使用Qwen进行标注

        流程:
        1. 构建prompt
        2. 调用模型生成标注
        3. 解析结果
        """
        with Timer() as timer:
            # 构建prompt
            prompt = self._build_prompt(text)

            # 生成标注
            response = self._generate(prompt)

            # 解析实体
            entities = parse_tagged_text(response)

        metadata = {
            "method": "method_a_qwen",
            "time_seconds": timer.elapsed,
            "token_count": 0,  # 本地模型无token消耗
            "entity_count": len(entities),
        }

        return AnnotationResult(
            original_text=text,
            entities=entities,
            relations=[],
            tagged_text=response,
            metadata=metadata
        )

    def _build_prompt(self, text: str) -> str:
        """构建Qwen prompt"""
        system_prompt = """你是《史记》语义标注专家。请对文言文进行实体标注。

标注要求:
1. 使用格式: 〖TYPE 实体文本〗
2. 消歧使用: 〖TYPE 显示名|规范名〗
3. 不要修改原文任何字符

实体类型:
- PERSON: 人物
- PLACE: 地名
- OFFICE: 官职
- ORG: 组织
- EVENT: 事件
- TIME: 时间

直接返回标注后的文本,不要解释。"""

        user_prompt = f"原文:\n{text}"

        # Qwen格式
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # 使用tokenizer的chat template
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        return prompt

    def _generate(self, prompt: str) -> str:
        """生成回复"""
        import torch

        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.get("max_length", 2048)
        )

        # 移动到设备
        device = self.config.get("device", "cuda")
        if device == "cuda":
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # 生成
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.config.get("max_length", 2048),
                do_sample=False,  # 贪心解码
                temperature=1.0,
                top_p=1.0,
            )

        # 解码
        response = self.tokenizer.decode(
            outputs[0][len(inputs.input_ids[0]):],
            skip_special_tokens=True
        )

        return response.strip()


def main():
    """主函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 加载配置
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 修改为Qwen
    qwen_config = config["local_model"].copy()
    qwen_config["type"] = "qwen"

    # 创建标注器
    annotator = QwenAnnotator(qwen_config)

    # 读取测试数据
    data_dir = Path(__file__).parent.parent / "data"
    test_file = data_dir / "test_corpus.txt"

    if not test_file.exists():
        print(f"测试数据不存在: {test_file}")
        return

    with open(test_file, encoding="utf-8") as f:
        text = f.read().strip()

    # 标注
    print("\n使用 Qwen2.5-7B 标注中...")
    result = annotator.annotate(text)

    # 输出结果
    print(f"\n原文:\n{result.original_text}\n")
    print(f"标注结果:\n{result.tagged_text}\n")
    print(f"统计:")
    print(f"  - 实体数: {result.metadata['entity_count']}")
    print(f"  - 耗时: {result.metadata['time_seconds']:.2f}秒")
    print(f"  - Token消耗: {result.metadata['token_count']}")

    # 保存结果
    output_dir = Path(__file__).parent.parent / "results"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "method_a_qwen_result.tagged.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result.tagged_text)

    print(f"\n结果已保存到: {output_file}")


if __name__ == "__main__":
    main()
