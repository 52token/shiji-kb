"""
方案C: 纯LLM标注(对照组)

直接使用大模型完成全部标注工作
"""

import os
import sys
import yaml
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    AnnotationResult,
    Timer,
    parse_tagged_text,
)


class PureLLMAnnotator:
    """纯LLM标注器"""

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        # LLM配置
        self.llm_config = config["llm"]

        # 初始化LLM客户端
        self._init_llm_client()

        # Token计数器
        self.total_tokens = 0

    def _init_llm_client(self):
        """初始化LLM客户端"""
        provider = self.llm_config["provider"]

        if provider == "anthropic":
            from anthropic import Anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY") or self.llm_config["api_key"]
            self.llm_client = Anthropic(api_key=api_key)
        elif provider == "openai":
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY") or self.llm_config["api_key"]
            self.llm_client = OpenAI(api_key=api_key)
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")

        self.logger.info(f"LLM客户端初始化成功 (provider={provider})")

    def annotate(self, text: str) -> AnnotationResult:
        """使用纯LLM进行标注"""
        with Timer() as timer:
            # 构建prompt
            prompt = self._build_prompt(text)

            # 调用LLM
            self.logger.info("调用LLM进行标注...")
            response = self._call_llm(prompt)

            # 解析结果
            entities = parse_tagged_text(response)

        metadata = {
            "method": "method_c_llm",
            "time_seconds": timer.elapsed,
            "token_count": self.total_tokens,
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
        """构建LLM提示"""
        return f"""你是《史记》语义标注专家。请对下面的文言文进行完整的实体标注。

原文:
{text}

标注要求:

1. **实体类型**:
   - PERSON: 人物(含字号/谥号)
   - PLACE: 地名(国/郡/县/城/山川等)
   - OFFICE: 官职/爵位
   - ORG: 组织/团体
   - EVENT: 重要事件
   - TIME: 时间(年号/季节/具体时间)
   - BOOK: 典籍/文献

2. **标注格式**:
   - 普通标注: 〖TYPE 实体文本〗
   - 消歧标注: 〖TYPE 显示名|规范名〗

   示例:
   - 〖PERSON 项羽〗
   - 〖PERSON 高祖|刘邦〗
   - 〖PLACE 咸阳〗
   - 〖OFFICE 丞相〗
   - 〖TIME 秦二世元年〗

3. **标注铁律**:
   - **绝对禁止修改原文任何字符**(不得增删改字符、标点、空格)
   - 只能在原文字符周围添加 〖TYPE 〗 标记
   - 消歧的"规范名"不改变显示文本
   - 标记去除后必须与原文逐字相同

4. **标注策略**:
   - 优先标注核心实体(人物/地名/官职)
   - 同一实体首次出现标全称,后续可简化
   - 疑难实体使用消歧语法
   - 避免过度标注(虚词/代词等不标)

请直接返回标注后的完整文本,不要有任何解释或说明。"""

    def _call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        provider = self.llm_config["provider"]

        if provider == "anthropic":
            response = self.llm_client.messages.create(
                model=self.llm_config["model"],
                max_tokens=self.llm_config["max_tokens"],
                temperature=self.llm_config["temperature"],
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # 统计token
            self.total_tokens += response.usage.input_tokens
            self.total_tokens += response.usage.output_tokens

            self.logger.info(
                f"Token使用: input={response.usage.input_tokens}, "
                f"output={response.usage.output_tokens}, "
                f"total={self.total_tokens}"
            )

            return response.content[0].text

        elif provider == "openai":
            response = self.llm_client.chat.completions.create(
                model=self.llm_config["model"],
                temperature=self.llm_config["temperature"],
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # 统计token
            self.total_tokens += response.usage.total_tokens

            self.logger.info(f"Token使用: {self.total_tokens}")

            return response.choices[0].message.content

        else:
            raise ValueError(f"不支持的provider: {provider}")


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

    # 创建纯LLM标注器
    annotator = PureLLMAnnotator(config)

    # 读取测试数据
    data_dir = Path(__file__).parent.parent / "data"
    test_file = data_dir / "test_corpus.txt"

    if not test_file.exists():
        print(f"测试数据不存在: {test_file}")
        print("请先创建测试数据")
        return

    with open(test_file, encoding="utf-8") as f:
        text = f.read().strip()

    # 标注
    print("\n使用纯LLM方案标注中...")
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

    output_file = output_dir / "method_c_llm_result.tagged.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result.tagged_text)

    print(f"\n结果已保存到: {output_file}")


if __name__ == "__main__":
    main()
