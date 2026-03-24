#!/usr/bin/env python3
"""
语义标签统一处理模块

定义史记知识库中使用的语义标签标准，并提供统一的处理函数。

标签标准（2024版）：
- 〖@人名〗 - 人名
- 〖%时间〗 - 时间表达
- 〖#地名〗 - 地名
- 〖$官职〗 - 官职
- 〖&战争〗 - 战争/事件名
- 〖;人名〗 - 上文已提及的人名

消歧格式：
- 〖@显示名|规范名〗 - 当显示名与规范名不同时使用
"""

import re
from typing import Dict, Tuple


# 标准语义标签定义
SEMANTIC_TAG_TYPES = {
    '@': ('person', '人名', '#c00'),
    '%': ('time', '时间', '#06c'),
    '#': ('place', '地名', '#080'),
    '$': ('office', '官职', '#660'),
    '&': ('war', '战争', '#690'),
    ';': ('ref', '上文提及', '#999'),
}


# 旧版标签映射（用于兼容旧数据）
LEGACY_TAG_MAPPING = {
    '=': '#',  # 旧版地名 -> 新版地名
    '^': '$',  # 旧版官职 -> 新版官职
    '•': '~',  # 旧版器物（暂时映射为其他）
    '{': '~',  # 旧版典籍（暂时映射为其他）
    "'": '~',  # 旧版邦国（暂时映射为其他）
    '~': '&',  # 旧版事件 -> 新版战争
    '?': '~',  # 旧版神话（暂时映射为其他）
    '!': '~',  # 旧版概念（暂时映射为其他）
    ':': '~',  # 旧版方位（暂时映射为其他）
    '[': '~',  # 旧版古物（暂时映射为其他）
    '+': '~',  # 旧版生物（暂时映射为其他）
}


def remove_semantic_tags(text: str, normalize_legacy: bool = False) -> str:
    """
    移除语义标签，只保留显示文本

    参数:
        text: 包含语义标签的文本
        normalize_legacy: 是否先将旧版标签转换为新标准（默认False，直接移除）

    返回:
        移除标签后的纯文本

    示例:
        "〖@武王〗伐〖#纣〗" -> "武王伐纣"
        "〖@姬发|周武王〗" -> "姬发"
    """
    if not text:
        return text

    # 如果需要，先规范化旧版标签
    if normalize_legacy:
        text = normalize_legacy_tags(text)

    # 处理消歧格式: 〖TYPE显示名|规范名〗 -> 显示名
    text = re.sub(r'〖[@%#\$&~;]\s*([^|〗]+)\|[^〗]+〗', r'\1', text)

    # 处理普通格式: 〖TYPE文本〗 -> 文本（TYPE是单字符标记）
    # 多次处理以应对嵌套标签
    for _ in range(3):  # 最多处理3层嵌套
        text = re.sub(r'〖[@%#\$&~;]\s*([^〗]+)〗', r'\1', text)

    # 清理残留的未闭合标签符号
    text = text.replace('〖', '').replace('〗', '')

    return text


def normalize_legacy_tags(text: str) -> str:
    """
    将旧版标签符号转换为新标准

    例如: 〖=长安〗 -> 〖#长安〗
    """
    if not text:
        return text

    for old_marker, new_marker in LEGACY_TAG_MAPPING.items():
        # 转换普通格式
        text = text.replace(f'〖{old_marker}', f'〖{new_marker}')
        # 转换消歧格式
        text = re.sub(
            f'〖{re.escape(old_marker)}\\s*([^〗]+)〗',
            f'〖{new_marker}\\1〗',
            text
        )

    return text


def render_tags_to_html(text: str, normalize_legacy: bool = True) -> str:
    """
    将语义标签转换为HTML span标签（保留标注，用于高亮显示）

    参数:
        text: 包含语义标签的文本
        normalize_legacy: 是否先将旧版标签转换为新标准

    返回:
        转换后的HTML文本

    示例:
        "〖@武王〗" -> '<span class="entity person" title="人名">武王</span>'
    """
    if not text:
        return text

    # 先规范化旧版标签
    if normalize_legacy:
        text = normalize_legacy_tags(text)

    # 处理消歧格式: 〖TYPE显示名|规范名〗 -> HTML（显示名）
    for marker, (css_class, title, color) in SEMANTIC_TAG_TYPES.items():
        # 消歧格式
        pattern = f'〖{re.escape(marker)}\\s*([^|〗]+)\\|[^〗]+〗'
        replacement = f'<span class="entity {css_class}" title="{title}">\\1</span>'
        text = re.sub(pattern, replacement, text)

    # 处理普通格式: 〖TYPE文本〗 -> HTML
    for marker, (css_class, title, color) in SEMANTIC_TAG_TYPES.items():
        pattern = f'〖{re.escape(marker)}\\s*([^〗]+)〗'
        replacement = f'<span class="entity {css_class}" title="{title}">\\1</span>'
        text = re.sub(pattern, replacement, text)

    # 处理其他未识别的标签（如 〖~xxx〗）
    text = re.sub(
        r'〖[~_\\]([^〗]+)〗',
        r'<span class="entity other" title="其他标注">\1</span>',
        text
    )

    # 清理不完整或未闭合的标签（源数据问题）
    text = text.replace('〖', '').replace('〗', '')

    return text


def get_entity_css_styles() -> str:
    """
    返回实体标注的统一CSS样式

    可在HTML页面的<style>标签中使用
    """
    css = """
        /* 语义标签实体样式 */
        .entity {
            font-weight: 500;
            border-bottom: 1px dotted;
            cursor: help;
        }
"""

    for marker, (css_class, title, color) in SEMANTIC_TAG_TYPES.items():
        css += f"""
        .entity.{css_class} {{
            color: {color};
            border-bottom-color: {color};
        }}
"""

    css += """
        .entity.other {
            color: #999;
            border-bottom-color: #999;
        }
"""

    return css


def extract_entities(text: str, normalize_legacy: bool = True) -> Dict[str, list]:
    """
    从文本中提取所有实体

    参数:
        text: 包含语义标签的文本
        normalize_legacy: 是否先规范化旧版标签

    返回:
        按类型分组的实体列表
        例如: {'person': ['武王', '纣'], 'place': ['朝歌']}
    """
    if not text:
        return {}

    if normalize_legacy:
        text = normalize_legacy_tags(text)

    entities = {}

    for marker, (css_class, title, color) in SEMANTIC_TAG_TYPES.items():
        # 提取消歧格式中的规范名
        pattern = f'〖{re.escape(marker)}\\s*[^|〗]+\\|([^〗]+)〗'
        canonical_names = re.findall(pattern, text)

        # 提取普通格式
        pattern = f'〖{re.escape(marker)}\\s*([^|〗]+)〗'
        display_names = re.findall(pattern, text)

        if canonical_names or display_names:
            entities[css_class] = list(set(canonical_names + display_names))

    return entities


# 便捷函数
def clean_text(text: str) -> str:
    """移除所有语义标签，返回纯文本（快捷方式）"""
    return remove_semantic_tags(text, normalize_legacy=True)


def html_with_highlights(text: str) -> str:
    """转换为带高亮的HTML（快捷方式）"""
    return render_tags_to_html(text, normalize_legacy=True)
