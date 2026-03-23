#!/usr/bin/env python3
"""修复嵌套刑法标注错误"""

import re
import sys

def fix_nested_legal(text):
    """修复嵌套的刑法标注"""
    fixes = []
    
    # Pattern 1: 〖[当〖[X〗〗 -> 〖[当X〗
    pattern1 = r'〖\[当〖\[([^〗]+)〗〗'
    for match in re.finditer(pattern1, text):
        fixes.append((match.group(0), f'〖[当{match.group(1)}〗'))
    
    # Pattern 2: 〖[腰〖[斩〗〗 -> 〖[腰斩〗
    pattern2 = r'〖\[腰〖\[斩〗〗'
    for match in re.finditer(pattern2, text):
        fixes.append((match.group(0), '〖[腰斩〗'))
    
    # Pattern 3: 〖[〖[X〗Y〗 -> 〖[XY〗 (斩首等)
    pattern3 = r'〖\[〖\[([^〗]+)〗([^〗]+)〗'
    for match in re.finditer(pattern3, text):
        fixes.append((match.group(0), f'〖[{match.group(1)}{match.group(2)}〗'))
    
    # Apply fixes
    result = text
    for old, new in fixes:
        result = result.replace(old, new)
    
    return result, len(fixes)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: fix_nested_legal.py <file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixed, count = fix_nested_legal(content)
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print(f"✓ {filepath}: 修复 {count} 处嵌套标注")
    else:
        print(f"  {filepath}: 无需修复")
