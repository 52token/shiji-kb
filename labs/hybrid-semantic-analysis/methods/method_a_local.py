"""
方案A: 纯本地NLP模型

支持:
- LTP (依存文法,哈工大)
- HanLP (依存文法)
- Qwen2.5-7B (小模型,需4-5GB显存)
- GLM-4-9B (小模型,需6-7GB显存)
"""

import sys
import yaml
import logging
from pathlib import Path
from typing import List, Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    Entity,
    AnnotationResult,
    Timer,
    entities_to_tagged_text,
)


class LocalNLPAnnotator:
    """本地NLP标注器基类"""

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def annotate(self, text: str) -> AnnotationResult:
        """标注文本"""
        raise NotImplementedError


class LTPAnnotator(LocalNLPAnnotator):
    """基于LTP的依存文法标注器"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载LTP模型"""
        try:
            from ltp import LTP
            device = self.config.get("device", "cuda")
            self.model = LTP(device=device)
            self.logger.info(f"LTP模型加载成功 (device={device})")
        except Exception as e:
            self.logger.error(f"LTP模型加载失败: {e}")
            raise

    def annotate(self, text: str) -> AnnotationResult:
        """
        使用LTP进行标注

        流程:
        1. 分词 + 词性标注
        2. 命名实体识别 (NER)
        3. 依存句法分析
        4. 规则提取实体
        """
        with Timer() as timer:
            # LTP处理
            result = self.model.pipeline(
                [text],
                tasks=["cws", "pos", "ner", "dep"]
            )

            # 提取实体
            entities = self._extract_entities(text, result)

            # 生成标注文本
            tagged_text = entities_to_tagged_text(text, entities)

        metadata = {
            "method": "method_a_ltp",
            "time_seconds": timer.elapsed,
            "token_count": 0,  # 本地模型无token消耗
            "entity_count": len(entities),
        }

        return AnnotationResult(
            original_text=text,
            entities=entities,
            relations=[],
            tagged_text=tagged_text,
            metadata=metadata
        )

    def _extract_entities(
        self,
        text: str,
        ltp_result: dict
    ) -> List[Entity]:
        """
        从LTP结果提取实体

        LTP NER标签:
        - Nh: 人名
        - Ni: 机构名
        - Ns: 地名
        """
        entities = []

        # 获取结果
        words = ltp_result["cws"][0]      # 分词结果
        pos = ltp_result["pos"][0]        # 词性
        ner = ltp_result["ner"][0]        # 命名实体

        # 计算每个词在原文中的位置
        offset = 0
        word_positions = []
        for word in words:
            start = text.find(word, offset)
            if start == -1:
                # 处理分词可能的误差
                start = offset
            end = start + len(word)
            word_positions.append((start, end))
            offset = end

        # 提取NER实体
        for (tag, start_idx, end_idx) in ner:
            # 映射LTP标签到我们的类型
            entity_type = self._map_ner_tag(tag)
            if entity_type is None:
                continue

            # 获取实体文本和位置
            entity_words = words[start_idx:end_idx + 1]
            entity_text = "".join(entity_words)

            # 计算在原文中的位置
            char_start = word_positions[start_idx][0]
            char_end = word_positions[end_idx][1]

            entities.append(Entity(
                text=entity_text,
                type=entity_type,
                start=char_start,
                end=char_end,
                confidence=0.9  # LTP NER置信度较高
            ))

        # 补充规则提取(词性标注)
        entities.extend(
            self._extract_by_pos(words, pos, word_positions)
        )

        # 去重(保留置信度高的)
        entities = self._deduplicate_entities(entities)

        return entities

    def _map_ner_tag(self, tag: str) -> Optional[str]:
        """映射LTP NER标签到我们的实体类型"""
        mapping = {
            "Nh": "PERSON",    # 人名
            "Ni": "ORG",       # 机构名
            "Ns": "PLACE",     # 地名
        }
        return mapping.get(tag)

    def _extract_by_pos(
        self,
        words: List[str],
        pos_tags: List[str],
        positions: List[tuple]
    ) -> List[Entity]:
        """
        基于词性标注提取额外实体

        常见词性:
        - nr: 人名
        - ns: 地名
        - nt: 机构名
        - nz: 其他专名
        """
        entities = []

        for i, (word, pos) in enumerate(zip(words, pos_tags)):
            entity_type = None

            if pos == "nr":
                entity_type = "PERSON"
            elif pos == "ns":
                entity_type = "PLACE"
            elif pos == "nt":
                entity_type = "ORG"
            elif pos == "nz":
                # 其他专名,需进一步判断
                entity_type = self._classify_special_name(word)

            if entity_type:
                start, end = positions[i]
                entities.append(Entity(
                    text=word,
                    type=entity_type,
                    start=start,
                    end=end,
                    confidence=0.7  # 词性标注置信度略低
                ))

        return entities

    def _classify_special_name(self, word: str) -> Optional[str]:
        """分类其他专名"""
        # 简单规则(可扩展)
        if word.endswith(("国", "郡", "县", "城", "邑")):
            return "PLACE"
        elif word.endswith(("王", "侯", "公", "君")):
            return "PERSON"
        elif word.endswith(("军", "师", "营", "部")):
            return "ORG"
        return None

    def _deduplicate_entities(
        self,
        entities: List[Entity]
    ) -> List[Entity]:
        """
        去除重叠实体,保留置信度高的

        策略:
        - 完全相同的实体,保留一个
        - 重叠的实体,保留置信度高的
        """
        if not entities:
            return []

        # 按置信度降序排序
        entities = sorted(
            entities,
            key=lambda e: (e.confidence, e.end - e.start),
            reverse=True
        )

        # 过滤重叠
        filtered = []
        occupied = set()  # 已占用的字符位置

        for entity in entities:
            # 检查是否重叠
            positions = set(range(entity.start, entity.end))
            if not (positions & occupied):
                filtered.append(entity)
                occupied.update(positions)

        # 按位置排序
        filtered = sorted(filtered, key=lambda e: e.start)

        return filtered


class HanLPAnnotator(LocalNLPAnnotator):
    """基于HanLP的标注器"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载HanLP模型"""
        try:
            import hanlp
            self.model = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)
            self.logger.info("HanLP模型加载成功")
        except Exception as e:
            self.logger.error(f"HanLP模型加载失败: {e}")
            raise

    def annotate(self, text: str) -> AnnotationResult:
        """使用HanLP进行标注"""
        # TODO: 实现HanLP标注逻辑(类似LTP)
        raise NotImplementedError("HanLP标注器待实现")


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

    local_config = config["local_model"]

    # 创建标注器
    model_type = local_config["type"]
    if model_type == "ltp":
        annotator = LTPAnnotator(local_config)
    elif model_type == "hanlp":
        annotator = HanLPAnnotator(local_config)
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")

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
    print(f"\n使用 {model_type.upper()} 标注中...")
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

    output_file = output_dir / f"method_a_{model_type}_result.tagged.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result.tagged_text)

    print(f"\n结果已保存到: {output_file}")


if __name__ == "__main__":
    main()
