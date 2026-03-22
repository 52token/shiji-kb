"""基础工具类"""

import re
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class Entity:
    """实体类"""
    text: str           # 实体文本
    type: str          # 实体类型(PERSON/PLACE/OFFICE等)
    start: int         # 起始位置
    end: int           # 结束位置
    confidence: float  # 置信度(0-1)
    canonical: str = None  # 规范名(用于消歧)


@dataclass
class Relation:
    """关系类"""
    head: Entity       # 头实体
    relation: str      # 关系类型
    tail: Entity       # 尾实体
    confidence: float  # 置信度


@dataclass
class AnnotationResult:
    """标注结果"""
    original_text: str           # 原文
    entities: List[Entity]       # 实体列表
    relations: List[Relation]    # 关系列表
    tagged_text: str            # 标注后文本
    metadata: Dict              # 元数据(耗时/token等)


class Timer:
    """计时器"""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        self.end_time = time.time()

    @property
    def elapsed(self) -> float:
        """返回耗时(秒)"""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time


def remove_tags(text: str) -> str:
    """
    移除标注标记,还原纯文本

    Args:
        text: 标注文本

    Returns:
        纯文本
    """
    # 移除消歧语法: 〖TYPE 显示名|规范名〗 → 显示名
    text = re.sub(r'〖[A-Z_]+\s+([^|〗]+)\|[^〗]+〗', r'\1', text)

    # 移除普通标记: 〖TYPE 文本〗 → 文本
    text = re.sub(r'〖[A-Z_]+\s+([^〗]+)〗', r'\1', text)

    return text


def verify_text_integrity(original: str, tagged: str) -> bool:
    """
    验证标注后文本完整性

    Args:
        original: 原文
        tagged: 标注文本

    Returns:
        是否一致
    """
    cleaned = remove_tags(tagged)
    return cleaned == original


def entities_to_tagged_text(text: str, entities: List[Entity]) -> str:
    """
    将实体列表转为标注文本

    Args:
        text: 原文
        entities: 实体列表

    Returns:
        标注文本
    """
    # 按位置排序,避免重叠
    entities = sorted(entities, key=lambda e: e.start)

    # 过滤重叠实体(保留置信度高的)
    filtered = []
    last_end = -1
    for entity in entities:
        if entity.start >= last_end:
            filtered.append(entity)
            last_end = entity.end

    # 从后往前插入标记(避免位置偏移)
    result = text
    for entity in reversed(filtered):
        # 提取实体文本
        entity_text = text[entity.start:entity.end]

        # 生成标记
        if entity.canonical and entity.canonical != entity_text:
            # 消歧语法
            tag = f"〖{entity.type} {entity_text}|{entity.canonical}〗"
        else:
            # 普通标记
            tag = f"〖{entity.type} {entity_text}〗"

        # 替换
        result = result[:entity.start] + tag + result[entity.end:]

    return result


def calculate_metrics(
    pred_entities: List[Entity],
    gold_entities: List[Entity]
) -> Dict[str, float]:
    """
    计算评估指标

    Args:
        pred_entities: 预测实体列表
        gold_entities: 标准答案实体列表

    Returns:
        指标字典 {precision, recall, f1}
    """
    # 转为集合(text, type, start, end)
    pred_set = {
        (e.text, e.type, e.start, e.end)
        for e in pred_entities
    }
    gold_set = {
        (e.text, e.type, e.start, e.end)
        for e in gold_entities
    }

    # 计算交集
    tp = len(pred_set & gold_set)
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)

    # 计算指标
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


def parse_tagged_text(tagged_text: str) -> List[Entity]:
    """
    解析标注文本,提取实体列表

    Args:
        tagged_text: 标注文本

    Returns:
        实体列表
    """
    entities = []
    plain_text = ""
    offset = 0

    # 正则匹配所有标记
    pattern = r'〖([A-Z_]+)\s+([^〗]+)〗'

    last_end = 0
    for match in re.finditer(pattern, tagged_text):
        entity_type = match.group(1)
        content = match.group(2)

        # 更新纯文本
        plain_text += tagged_text[last_end:match.start()]

        # 解析消歧语法
        if '|' in content:
            display_name, canonical_name = content.split('|', 1)
        else:
            display_name = content
            canonical_name = None

        # 计算实体在纯文本中的位置
        start = len(plain_text)
        end = start + len(display_name)

        # 创建实体
        entities.append(Entity(
            text=display_name,
            type=entity_type,
            start=start,
            end=end,
            confidence=1.0,
            canonical=canonical_name
        ))

        # 更新纯文本
        plain_text += display_name
        last_end = match.end()

    # 添加剩余文本
    plain_text += tagged_text[last_end:]

    return entities
