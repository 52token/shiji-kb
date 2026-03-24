#!/usr/bin/env python3
"""
从标注文件中提取段落结构和语义关系

用于生成段落级别的结构化数据
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any


def extract_paragraph_structure(tagged_file: Path) -> Dict[str, Any]:
    """提取段落结构"""

    with open(tagged_file, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    paragraphs = []
    current_section = None
    current_subsection = None

    for i, line in enumerate(lines):
        # 大节标题（如：## 〖@黄帝〗）
        if line.startswith('## '):
            # 提取标签内的文本作为标题
            match = re.search(r'〖[@#\$%&]\s*([^〗|]+)(?:\|[^〗]+)?〗', line)
            if match:
                current_section = match.group(1).strip()
            else:
                current_section = line[3:].strip()
            current_subsection = None

        # 小节标题（如：### 兴起与征讨）
        elif line.startswith('### '):
            current_subsection = line[4:].strip()

        # 段落标记（如：[1], [1.1], [11.5]）
        elif line.startswith('[') and ']' in line:
            match = re.match(r'\[([^\]]+)\]\s*(.+)', line)
            if match:
                anchor = match.group(1)
                first_text = match.group(2)

                # 提取完整段落内容（多行）
                full_text = first_text
                j = i + 1
                while j < len(lines) and lines[j] and not lines[j].startswith('[') and not lines[j].startswith('#'):
                    if not lines[j].startswith('-') and not lines[j].startswith('---'):  # 不包括列表项和分隔符
                        full_text += ' ' + lines[j]
                    j += 1

                # 保留一些标签以便理解（只移除标签符号，保留内容）
                def clean_tags(text):
                    # 保留标签内的内容
                    text = re.sub(r'〖[@%#\$&~*;!+•?_\^=:\[]\s*([^|〗]+)(?:\|[^〗]+)?〗', r'\1', text)
                    # 移除动作标签
                    text = re.sub(r'⟦[^⟧]+⟧', '', text)
                    return text.strip()

                full_clean = clean_tags(full_text)

                # 截取摘要
                summary = full_clean[:100] + '...' if len(full_clean) > 100 else full_clean

                paragraphs.append({
                    'anchor': anchor,
                    'section': current_section if current_section else '',
                    'subsection': current_subsection if current_subsection else '',
                    'summary': summary,
                    'full_text': full_clean[:400]  # 最多400字
                })

    return {
        'chapter': tagged_file.stem.replace('.tagged', ''),
        'paragraphs': paragraphs
    }


def infer_relations(paragraphs: List[Dict]) -> List[Dict]:
    """推断段落之间的语义关系（简单规则）"""

    relations = []

    for i in range(len(paragraphs) - 1):
        curr = paragraphs[i]
        next_para = paragraphs[i + 1]

        # 规则1：同一大节内，相邻段落为时序关系
        if curr['section'] == next_para['section']:
            # 如果都是帝王段落（section是人名），则为继承关系
            if curr['section'] and '帝' in curr['section']:
                relations.append({
                    'source': curr['anchor'],
                    'target': next_para['anchor'],
                    'type': 'temporal',
                    'subtype': 'succession',
                    'description': f"{curr['section']}之后，{next_para['section']}继位"
                })
            else:
                relations.append({
                    'source': curr['anchor'],
                    'target': next_para['anchor'],
                    'type': 'temporal',
                    'subtype': 'sequential',
                    'description': f"段落{curr['anchor']}之后的相关叙述"
                })

        # 规则2：不同section，检查是否为继承
        elif curr['section'] != next_para['section']:
            if '帝' in str(curr['section']) and '帝' in str(next_para['section']):
                relations.append({
                    'source': curr['anchor'],
                    'target': next_para['anchor'],
                    'type': 'temporal',
                    'subtype': 'succession',
                    'description': f"{curr['section']}之后，{next_para['section']}继位"
                })

    # 特殊关系：太史公曰为总结
    for para in paragraphs:
        if '太史公曰' in str(para.get('section', '')):
            relations.append({
                'source': para['anchor'],
                'target': 'all',
                'type': 'hierarchy',
                'subtype': 'summary',
                'description': '太史公总结全篇'
            })

    return relations


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    tagged_file = project_root / 'chapter_md' / '001_五帝本纪.tagged.md'
    output_file = project_root / 'kg' / 'structure' / 'data' / 'paragraph_relations_001.json'

    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 提取段落结构
    structure = extract_paragraph_structure(tagged_file)

    # 推断关系
    relations = infer_relations(structure['paragraphs'])

    # 组合数据
    result = {
        'chapter': structure['chapter'],
        'total_paragraphs': len(structure['paragraphs']),
        'paragraphs': structure['paragraphs'],
        'relations': relations
    }

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 已提取 {result['total_paragraphs']} 个段落")
    print(f"✅ 已推断 {len(relations)} 个关系")
    print(f"✅ 数据已保存到: {output_file}")

    # 打印统计
    sections = set(p['section'] for p in structure['paragraphs'] if p['section'])
    print(f"\n大节数: {len(sections)}")
    for section in sorted(sections):
        count = sum(1 for p in structure['paragraphs'] if p['section'] == section)
        print(f"  - {section}: {count}段")


if __name__ == '__main__':
    main()
