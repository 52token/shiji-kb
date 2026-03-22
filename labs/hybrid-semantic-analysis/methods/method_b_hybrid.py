"""
方案B: 混合方案(本地模型粗标注 + LLM精炼)

策略:
1. 本地模型快速标注90%常见实体
2. 识别低置信度/复杂实体
3. LLM只处理疑难部分
"""

import os
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
    entities_to_tagged_text,
    remove_tags,
)

# 导入方案A的本地标注器
from method_a_local import LTPAnnotator


class HybridAnnotator:
    """混合标注器"""

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        # 初始化本地标注器
        local_config = config["local_model"]
        model_type = local_config["type"]

        if model_type == "ltp":
            self.local_annotator = LTPAnnotator(local_config)
        else:
            raise ValueError(f"混合方案暂不支持: {model_type}")

        # LLM配置
        self.llm_config = config["llm"]
        self.hybrid_config = config["hybrid"]

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
        """
        混合标注流程

        1. 本地模型粗标注
        2. 识别需要LLM处理的部分
        3. LLM精炼/补充标注
        4. 合并结果
        """
        with Timer() as timer:
            # 步骤1: 本地模型粗标注
            self.logger.info("步骤1: 本地模型粗标注...")
            local_result = self.local_annotator.annotate(text)

            # 步骤2: 识别需要LLM处理的部分
            self.logger.info("步骤2: 识别疑难部分...")
            llm_required_parts = self._identify_llm_required(
                text,
                local_result.entities
            )

            # 步骤3: LLM精炼
            llm_entities = []
            if llm_required_parts:
                self.logger.info(f"步骤3: LLM处理 {len(llm_required_parts)} 个片段...")
                llm_entities = self._refine_with_llm(
                    text,
                    llm_required_parts,
                    local_result.entities
                )

            # 步骤4: 合并结果
            self.logger.info("步骤4: 合并结果...")
            final_entities = self._merge_entities(
                local_result.entities,
                llm_entities
            )

            # 生成标注文本
            tagged_text = entities_to_tagged_text(text, final_entities)

        metadata = {
            "method": "method_b_hybrid",
            "time_seconds": timer.elapsed,
            "token_count": self.total_tokens,
            "entity_count": len(final_entities),
            "local_entity_count": len(local_result.entities),
            "llm_entity_count": len(llm_entities),
            "llm_required_parts": len(llm_required_parts),
        }

        return AnnotationResult(
            original_text=text,
            entities=final_entities,
            relations=[],
            tagged_text=tagged_text,
            metadata=metadata
        )

    def _identify_llm_required(
        self,
        text: str,
        local_entities: List[Entity]
    ) -> List[tuple]:
        """
        识别需要LLM处理的部分

        Returns:
            List[(start, end, reason)] 需要处理的文本片段
        """
        required = []
        threshold = self.hybrid_config["confidence_threshold"]
        llm_only_types = self.hybrid_config.get("llm_only_types", [])

        # 策略1: 低置信度实体
        for entity in local_entities:
            if entity.confidence < threshold:
                required.append((
                    entity.start,
                    entity.end,
                    f"low_confidence_{entity.type}"
                ))

        # 策略2: 特定类型(如复杂关系/事件)
        # 这里简化处理,识别未覆盖的长句子
        covered = set()
        for entity in local_entities:
            covered.update(range(entity.start, entity.end))

        # 查找未覆盖的长段落
        sentences = text.split("。")
        offset = 0
        for sentence in sentences:
            if not sentence.strip():
                offset += len(sentence) + 1
                continue

            start = offset
            end = offset + len(sentence)

            # 检查覆盖率
            sentence_positions = set(range(start, end))
            covered_rate = len(sentence_positions & covered) / len(sentence_positions)

            # 覆盖率低于50%且句子较长,可能包含复杂实体
            if covered_rate < 0.5 and len(sentence) > 20:
                required.append((start, end, "low_coverage"))

            offset = end + 1

        # 去重合并
        required = self._merge_ranges(required)

        return required

    def _merge_ranges(self, ranges: List[tuple]) -> List[tuple]:
        """合并重叠的范围"""
        if not ranges:
            return []

        # 按起始位置排序
        ranges = sorted(ranges, key=lambda x: x[0])

        merged = [ranges[0]]
        for start, end, reason in ranges[1:]:
            last_start, last_end, last_reason = merged[-1]

            # 如果重叠,合并
            if start <= last_end:
                merged[-1] = (
                    last_start,
                    max(end, last_end),
                    f"{last_reason}+{reason}"
                )
            else:
                merged.append((start, end, reason))

        return merged

    def _refine_with_llm(
        self,
        text: str,
        parts: List[tuple],
        local_entities: List[Entity]
    ) -> List[Entity]:
        """
        使用LLM精炼标注

        Args:
            text: 原文
            parts: 需要处理的片段 [(start, end, reason)]
            local_entities: 本地标注的实体(用于上下文)

        Returns:
            LLM标注的实体列表
        """
        llm_entities = []

        for start, end, reason in parts:
            # 提取片段
            fragment = text[start:end]

            # 构建prompt
            prompt = self._build_llm_prompt(fragment, reason)

            # 调用LLM
            try:
                response = self._call_llm(prompt)
                self.logger.debug(f"LLM响应: {response}")

                # 解析LLM返回的实体
                entities = self._parse_llm_response(
                    response,
                    fragment,
                    start
                )
                llm_entities.extend(entities)

            except Exception as e:
                self.logger.error(f"LLM调用失败: {e}")

        return llm_entities

    def _build_llm_prompt(self, fragment: str, reason: str) -> str:
        """构建LLM提示"""
        return f"""请对下面的文言文片段进行实体标注。

文本:
{fragment}

标注要求:
1. 识别所有实体(人物/地点/官职/事件等)
2. 使用格式: 〖TYPE 实体文本〗
3. 如需消歧,使用: 〖TYPE 显示名|规范名〗
4. 不要修改原文任何字符

实体类型:
- PERSON: 人物
- PLACE: 地点
- OFFICE: 官职
- ORG: 组织
- EVENT: 事件
- TIME: 时间

直接返回标注后的文本,不要有任何解释。"""

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

            return response.choices[0].message.content

        else:
            raise ValueError(f"不支持的provider: {provider}")

    def _parse_llm_response(
        self,
        response: str,
        fragment: str,
        offset: int
    ) -> List[Entity]:
        """
        解析LLM返回的标注文本

        Args:
            response: LLM返回的标注文本
            fragment: 原始片段
            offset: 片段在全文中的偏移量

        Returns:
            实体列表(位置已调整为全文坐标)
        """
        from utils import parse_tagged_text

        # 解析实体
        entities = parse_tagged_text(response)

        # 调整位置为全文坐标
        for entity in entities:
            entity.start += offset
            entity.end += offset

        return entities

    def _merge_entities(
        self,
        local_entities: List[Entity],
        llm_entities: List[Entity]
    ) -> List[Entity]:
        """
        合并本地和LLM标注的实体

        策略:
        - 对于重叠部分,优先使用LLM结果
        - 去除完全重复的实体
        """
        # 标记LLM覆盖的区域
        llm_covered = set()
        for entity in llm_entities:
            llm_covered.update(range(entity.start, entity.end))

        # 过滤本地实体(去除LLM已覆盖的)
        filtered_local = []
        for entity in local_entities:
            entity_positions = set(range(entity.start, entity.end))
            # 如果与LLM实体重叠超过50%,丢弃
            overlap = len(entity_positions & llm_covered)
            if overlap / len(entity_positions) < 0.5:
                filtered_local.append(entity)

        # 合并
        merged = filtered_local + llm_entities

        # 按位置排序
        merged = sorted(merged, key=lambda e: e.start)

        return merged


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

    # 创建混合标注器
    annotator = HybridAnnotator(config)

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
    print("\n使用混合方案标注中...")
    result = annotator.annotate(text)

    # 输出结果
    print(f"\n原文:\n{result.original_text}\n")
    print(f"标注结果:\n{result.tagged_text}\n")
    print(f"统计:")
    print(f"  - 总实体数: {result.metadata['entity_count']}")
    print(f"  - 本地实体数: {result.metadata['local_entity_count']}")
    print(f"  - LLM实体数: {result.metadata['llm_entity_count']}")
    print(f"  - LLM处理片段数: {result.metadata['llm_required_parts']}")
    print(f"  - 耗时: {result.metadata['time_seconds']:.2f}秒")
    print(f"  - Token消耗: {result.metadata['token_count']}")

    # 保存结果
    output_dir = Path(__file__).parent.parent / "results"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "method_b_hybrid_result.tagged.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result.tagged_text)

    print(f"\n结果已保存到: {output_file}")


if __name__ == "__main__":
    main()
