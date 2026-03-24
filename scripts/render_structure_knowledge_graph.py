#!/usr/bin/env python3
"""
生成交互式知识图谱可视化（使用vis.js）
"""

import json
from pathlib import Path

def generate_paragraph_title(para):
    """为段落生成4-6字的标题"""
    anchor = para['anchor']
    summary = para['summary']
    section = para['section']

    # 预定义的标题映射
    title_map = {
        '1': '黄帝出身', '1.1': '征伐诸侯', '1.2': '擒蚩尤', '1.3': '为天子',
        '3': '治理天下', '4': '黄帝子嗣', '4.1': '嫘祖二子', '4.2': '黄帝崩',
        '5': '颛顼德行', '6': '颛顼崩',
        '7': '帝喾世系', '8': '帝喾德行', '9': '帝喾崩',
        '10': '帝尧德行', '11': '制定历法', '11.5': '闰月四时', '13.8': '尧选舜',
        '14': '舜摄政', '14.1': '巡狩礼制', '14.2': '刑法教化',
        '15': '惩四罪', '15.5': '天下服',
        '16': '尧崩', '16.1': '授舜天下', '16.2': '舜让辟',
        '17': '舜世系', '18': '父弟欲杀', '19': '舜事亲孝',
        '20': '尧妻二女', '20.1': '焚廪脱险', '20.2': '实井逃生', '20.3': '复事瞽叟',
        '21': '八恺八元', '22.6': '流四凶',
        '23': '舜入麓', '23.1': '举十贤', '23.2': '分职任能', '23.3': '三年考功',
        '24': '群臣成功', '25': '舜崩', '25.1': '舜让禹', '25.2': '不敢专',
        '26': '五帝世系', '27': '太史公曰'
    }

    if anchor in title_map:
        return title_map[anchor]

    # 默认：使用section前4字
    return section[:4]

def generate_html(json_path, output_path):
    """生成HTML页面"""

    # 读取JSON数据
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    paragraphs = data['paragraphs']
    relations = data['relations']

    # 关系类型配置（添加2字简称）
    relation_config = {
        'temporal': {'color': '#999999', 'name': '时序关系', 'short_name': '时序', 'width': 5, 'dashes': False},  # 最粗
        'causal': {'color': '#e74c3c', 'name': '因果关系', 'short_name': '因果', 'width': 3, 'dashes': False},
        'genealogy': {'color': '#9b59b6', 'name': '世系关系', 'short_name': '世系', 'width': 4, 'dashes': False},
        'hierarchy': {'color': '#3498db', 'name': '总分关系', 'short_name': '总分', 'width': 2, 'dashes': [5, 5]},
        'parallel': {'color': '#2ecc71', 'name': '并列关系', 'short_name': '并列', 'width': 2, 'dashes': [10, 5]},
        'contrast': {'color': '#e67e22', 'name': '对比关系', 'short_name': '对比', 'width': 3, 'dashes': False},
        'meta': {'color': '#95a5a6', 'name': '元评论', 'short_name': '评论', 'width': 2, 'dashes': [2, 2]},
        'elaboration': {'color': '#1abc9c', 'name': '补充说明', 'short_name': '补充', 'width': 2, 'dashes': False}
    }

    # 节点颜色（按section）
    section_colors = {
        '黄帝': '#FFD700',
        '帝颛顼': '#87CEEB',
        '帝喾': '#98FB98',
        '帝尧': '#FFA07A',
        '帝舜': '#DDA0DD',
        '举贤任能': '#F0E68C',
        '五帝': '#E0E0E0',
        '太史公': '#D3D3D3'
    }

    # 构建节点数据（JSON格式）
    nodes = []
    for para in paragraphs:
        section_color = section_colors.get(para['section'], '#cccccc')

        # 生成段落标题
        para_title = generate_paragraph_title(para)

        # 根据段落字数计算节点大小（字数越多，节点越大）
        char_count = len(para['full_text'])
        # 基础大小 + 按字数缩放（每100字增加1单位）
        # 整体缩小：基础从20开始，最大不超过35
        size = min(20 + (char_count / 100), 35)
        size = max(size, 15)  # 最小15

        # 构建纯文本tooltip（不使用HTML标签，使用换行）
        subsection_text = para.get('subsection', '')
        tooltip_parts = [
            f"[{para['anchor']}] {para_title}",
            f"章节: {para['section']}"
        ]
        if subsection_text:
            tooltip_parts.append(f"小节: {subsection_text}")
        tooltip_parts.append('')  # 空行
        tooltip_parts.append(para['summary'][:80] + ('...' if len(para['summary']) > 80 else ''))

        tooltip = '\\n'.join(tooltip_parts)

        # 使用换行符将编号和标题分开：第一行在圆圈内，第二行在圆圈下方
        nodes.append({
            'id': para['anchor'],
            'label': para['anchor'] + '\\n' + para_title,  # 编号\n标题
            'title': tooltip,  # 纯文本tooltip
            'group': para['section'],
            'color': section_color,
            'size': size,
            'font': {
                'size': 10,  # 编号字号
                'color': '#000'
            }
        })

    # 构建边数据（JSON格式）
    edges = []
    edge_counter = 0  # 用于生成唯一ID
    for rel in relations:
        rel_type = rel['type']
        config = relation_config.get(rel_type, {'color': '#999', 'short_name': '关系', 'width': 1, 'dashes': False})

        # 使用计数器生成唯一ID，避免重复
        edge_counter += 1
        edge_id = f"edge_{edge_counter}"

        edge = {
            'id': edge_id,  # 唯一ID
            'from': rel['source'],
            'to': rel['target'],
            'color': config['color'],
            'width': config['width'],
            'title': rel.get('description', config['name']),  # tooltip显示详细描述
            'label': config['short_name'],  # 在边上显示2字关系名
            'arrows': 'to',
            'smooth': {'type': 'curvedCW', 'roundness': 0.2},
            'font': {
                'size': 9,
                'color': config['color'],
                'strokeWidth': 0,
                'align': 'top',  # 文字在边的上方，避免与箭头重叠
                'background': 'rgba(255,255,255,0.7)',  # 半透明白色背景
                'vadjust': -5  # 垂直向上偏移5像素
            },
            # 保存原始的from-to信息，用于后续的悬停效果
            'original_key': rel['source'] + '-' + rel['target']
        }

        if config['dashes']:
            edge['dashes'] = config['dashes']

        edges.append(edge)

    # 统计数据
    relation_stats = {}
    for rel in relations:
        rel_type = rel['type']
        if rel_type not in relation_stats:
            relation_stats[rel_type] = 0
        relation_stats[rel_type] += 1

    # 生成HTML
    # 先将nodes和edges转为JSON字符串
    nodes_json = json.dumps(nodes, ensure_ascii=False, indent=2)
    edges_json = json.dumps(edges, ensure_ascii=False, indent=2)

    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>《史记·五帝本纪》段落关系知识图谱</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network@9.1.2/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            font-family: "Songti SC", "SimSun", "Microsoft YaHei", sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }}

        .header {{
            background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}

        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2em;
        }}

        .header p {{
            margin: 5px 0;
            opacity: 0.9;
        }}

        .container {{
            display: flex;
            height: calc(100vh - 140px);
        }}

        .sidebar {{
            width: 300px;
            background: white;
            padding: 20px;
            overflow-y: auto;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        }}

        .sidebar h3 {{
            color: #8B4513;
            border-bottom: 2px solid #8B4513;
            padding-bottom: 10px;
            margin-top: 0;
        }}

        .stats-item {{
            margin: 10px 0;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 5px;
            border-left: 3px solid #8B4513;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 0.9em;
        }}

        .legend-color {{
            width: 30px;
            height: 3px;
            margin-right: 10px;
        }}

        .legend-color.dashed {{
            background: repeating-linear-gradient(
                to right,
                currentColor 0px,
                currentColor 5px,
                transparent 5px,
                transparent 10px
            );
        }}

        .section-legend {{
            margin-top: 20px;
        }}

        .section-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 0.9em;
        }}

        .section-circle {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }}

        #graph {{
            flex: 1;
            background: white;
            min-height: 600px;
            height: 100%;
        }}

        .controls {{
            padding: 15px;
            background: white;
            border-top: 1px solid #ddd;
            display: flex;
            justify-content: center;
            gap: 10px;
        }}

        .btn {{
            padding: 8px 16px;
            background: #8B4513;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            transition: background 0.3s;
        }}

        .btn:hover {{
            background: #A0522D;
        }}

        .filter-group {{
            margin: 15px 0;
        }}

        .filter-group label {{
            display: flex;
            align-items: center;
            margin: 5px 0;
            cursor: pointer;
            font-size: 0.9em;
        }}

        .filter-group input[type="checkbox"] {{
            margin-right: 8px;
        }}

        .notice {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 10px;
            margin: 15px 0;
            border-radius: 5px;
            font-size: 0.85em;
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>《史记·五帝本纪》段落关系知识图谱</h1>
        <p>44个段落 × 101个关系 × 8种关系类型</p>
        <p style="font-size: 0.9em;">SKILL-02d: 段落语义关系建模</p>
    </div>

    <div class="container">
        <div class="sidebar">
            <h3>📊 统计数据</h3>
            <div class="stats-item">
                <strong>总段落数</strong>: {len(paragraphs)}个<br>
                <strong>总关系数</strong>: {len(relations)}个<br>
                <strong>大节数</strong>: 8个<br>
                <strong>关系类型</strong>: 8种
            </div>

            <h3>🎨 关系类型图例</h3>
'''

    # 添加关系图例
    for rel_type, config in relation_config.items():
        count = relation_stats.get(rel_type, 0)
        dashed_class = 'dashed' if config['dashes'] else ''
        html += f'''
            <div class="legend-item">
                <div class="legend-color {dashed_class}" style="color: {config['color']}; background: {config['color']}; width: 40px; height: {config['width']}px;"></div>
                <span>{config['name']} ({count})</span>
            </div>'''

    html += '''
            <h3>📖 章节图例</h3>
            <div class="section-legend">
'''

    # 添加章节图例
    for section, color in section_colors.items():
        html += f'''
                <div class="section-item">
                    <div class="section-circle" style="background: {color};"></div>
                    <span>{section}</span>
                </div>'''

    html += '''
            </div>

            <h3>🔍 关系筛选</h3>
            <div class="filter-group">
                <label>
                    <input type="checkbox" class="relation-filter" value="temporal" checked>
                    时序关系
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="causal" checked>
                    因果关系
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="genealogy" checked>
                    世系关系
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="hierarchy" checked>
                    总分关系
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="parallel" checked>
                    并列关系
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="contrast" checked>
                    对比关系
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="meta" checked>
                    元评论
                </label>
                <label>
                    <input type="checkbox" class="relation-filter" value="elaboration" checked>
                    补充说明
                </label>
            </div>

            <div class="notice">
                <strong>💡 操作提示</strong><br>
                • 拖动节点改变位置<br>
                • 滚轮缩放视图<br>
                • 悬停节点查看详情<br>
                • <strong>双击节点跳转到原文</strong><br>
                • 使用筛选器控制显示的关系类型
            </div>
        </div>

        <div id="graph"></div>
    </div>

    <div class="controls">
        <button class="btn" onclick="network.fit()">适应视图</button>
        <button class="btn" onclick="resetLayout()">重置布局</button>
        <button class="btn" onclick="togglePhysics()">切换物理引擎</button>
    </div>

    <script>
        // 数据
        const nodesData = ''' + nodes_json + ''';
        const edgesData = ''' + edges_json + ''';

        // 创建数据集
        const nodes = new vis.DataSet(nodesData);
        const edges = new vis.DataSet(edgesData);

        // 网络配置
        const options = {
            nodes: {
                shape: 'circle',  // 使用circle而不是dot，可以在内部显示文字
                borderWidth: 2,
                borderWidthSelected: 4,
                shadow: true,
                font: {
                    size: 10,
                    color: '#000',
                    face: 'arial',
                    vadjust: 0
                },
                labelHighlightBold: false
            },
            edges: {
                smooth: {
                    type: 'curvedCW',
                    roundness: 0.2
                },
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 0.5
                    }
                },
                shadow: true
            },
            physics: {
                enabled: true,
                stabilization: {
                    enabled: true,
                    iterations: 500,
                    updateInterval: 25,
                    fit: true
                }
            },
            layout: {
                improvedLayout: true
            },
            interaction: {
                hover: true,
                tooltipDelay: 100,
                navigationButtons: true,
                keyboard: true
            }
        };

        // 创建网络
        const container = document.getElementById('graph');
        console.log('Container:', container);
        console.log('Nodes count:', nodesData.length);
        console.log('Edges count:', edgesData.length);

        const data = {
            nodes: nodes,
            edges: edges
        };
        const network = new vis.Network(container, data, options);

        console.log('Network created');

        // 网络初始化完成后适应视图
        network.once('afterDrawing', function() {
            console.log('First drawing complete');
            network.fit();
        });

        // 鼠标悬停效果：根据距离调整节点和边的透明度
        let hoveredNodeId = null;

        network.on("hoverNode", function(params) {
            hoveredNodeId = params.node;
            updateNodesAndEdgesOpacity(hoveredNodeId);
        });

        network.on("blurNode", function(params) {
            hoveredNodeId = null;
            resetNodesAndEdgesOpacity();
        });

        // 计算图中两个节点之间的最短路径距离（BFS）
        function getShortestDistance(fromNode, toNode) {
            if (fromNode === toNode) return 0;

            const visited = new Set();
            const queue = [{node: fromNode, distance: 0}];
            visited.add(fromNode);

            while (queue.length > 0) {
                const {node, distance} = queue.shift();

                // 获取当前节点的所有邻居
                const connectedEdges = edgesData.filter(e => e.from === node || e.to === node);
                for (const edge of connectedEdges) {
                    const neighbor = edge.from === node ? edge.to : edge.from;
                    if (neighbor === toNode) {
                        return distance + 1;
                    }
                    if (!visited.has(neighbor)) {
                        visited.add(neighbor);
                        queue.push({node: neighbor, distance: distance + 1});
                    }
                }
            }

            return Infinity; // 不连通
        }

        function updateNodesAndEdgesOpacity(hoveredId) {
            // 计算所有节点到悬停节点的距离
            const distances = {};
            let maxDistance = 0;

            nodesData.forEach(node => {
                const dist = getShortestDistance(hoveredId, node.id);
                distances[node.id] = dist;
                if (dist !== Infinity && dist > maxDistance) {
                    maxDistance = dist;
                }
            });

            // 更新节点透明度
            const updatedNodes = nodesData.map(node => {
                const dist = distances[node.id];
                let opacity = 1.0;

                if (dist === 0) {
                    opacity = 1.0; // 悬停节点自己
                } else if (dist === Infinity) {
                    opacity = 0.1; // 不连通的节点
                } else {
                    // 根据距离计算透明度：距离越远越淡
                    opacity = Math.max(0.15, 1.0 - (dist / (maxDistance + 1)) * 0.85);
                }

                return {
                    id: node.id,
                    opacity: opacity
                };
            });

            nodes.update(updatedNodes);

            // 更新边的透明度和宽度
            const updatedEdges = edgesData.map(edge => {
                const fromDist = distances[edge.from] || Infinity;
                const toDist = distances[edge.to] || Infinity;

                // 直接相关的边（距离为0-1之间）
                const isDirect = (fromDist === 0 && toDist === 1) || (fromDist === 1 && toDist === 0);

                let opacity, width;
                if (isDirect) {
                    opacity = 1.0;
                    width = edge.width * 2; // 加粗
                } else {
                    // 根据两端节点的最近距离计算透明度
                    const minDist = Math.min(fromDist, toDist);
                    if (minDist === Infinity) {
                        opacity = 0.05;
                    } else {
                        opacity = Math.max(0.1, 1.0 - (minDist / (maxDistance + 1)) * 0.9);
                    }
                    width = edge.width;
                }

                return {
                    id: edge.id,  // 使用边的唯一ID
                    opacity: opacity,
                    width: width
                };
            });

            edges.update(updatedEdges);
        }

        function resetNodesAndEdgesOpacity() {
            // 恢复所有节点
            const updatedNodes = nodesData.map(node => ({
                id: node.id,
                opacity: 1.0
            }));
            nodes.update(updatedNodes);

            // 恢复所有边
            const updatedEdges = edgesData.map(edge => ({
                id: edge.id,  // 使用边的唯一ID
                opacity: 1.0,
                width: edge.width
            }));
            edges.update(updatedEdges);
        }

        // 物理引擎开关
        let physicsEnabled = true;
        function togglePhysics() {
            physicsEnabled = !physicsEnabled;
            network.setOptions({ physics: { enabled: physicsEnabled } });
        }

        // 重置布局
        function resetLayout() {
            network.setOptions({ physics: { enabled: true } });
            setTimeout(() => {
                network.fit();
            }, 1000);
        }

        // 关系筛选
        const relationTypeMap = new Map();
        const colorToType = {
            '#999999': 'temporal',
            '#e74c3c': 'causal',
            '#9b59b6': 'genealogy',
            '#3498db': 'hierarchy',
            '#2ecc71': 'parallel',
            '#e67e22': 'contrast',
            '#95a5a6': 'meta',
            '#1abc9c': 'elaboration'
        };

        edgesData.forEach((edge, index) => {
            relationTypeMap.set(edge.id, colorToType[edge.color] || 'unknown');
        });

        document.querySelectorAll('.relation-filter').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const checkedTypes = Array.from(document.querySelectorAll('.relation-filter:checked'))
                    .map(cb => cb.value);

                const filteredEdges = edgesData.filter(edge => {
                    const edgeType = relationTypeMap.get(edge.id);
                    return checkedTypes.includes(edgeType);
                });

                edges.clear();
                edges.add(filteredEdges);
            });
        });

        // 节点单击事件
        network.on("selectNode", function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                console.log('Selected node:', nodeId);
            }
        });

        // 双击节点跳转到段落详情页
        network.on("doubleClick", function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                // 跳转到五帝本纪页面，带锚点
                const url = '../001_五帝本纪.html#para-' + nodeId;
                window.open(url, '_blank');
            }
        });

        // 稳定后适应视图
        network.once('stabilized', function() {
            network.fit();
        });
    </script>
</body>
</html>'''

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'✅ 知识图谱HTML已生成: {output_path}')
    print(f'   节点数: {len(nodes)}')
    print(f'   边数: {len(edges)}')
    print(f'   关系类型: {len(relation_config)}种')

def main():
    json_path = Path('/home/baojie/work/shiji-kb/kg/structure/data/paragraph_relations_001_enhanced.json')
    output_path = Path('/home/baojie/work/shiji-kb/docs/special/structure.html')

    generate_html(json_path, output_path)

if __name__ == '__main__':
    main()
