# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 10:10:05 2025

@author: Yinghong
"""

import pandas as pd
import networkx as nx
from pyvis.network import Network
import os
import json

# ========= 1. 读取并清理数据 =========
df = pd.read_csv('SoilMechanicsMarkDown.csv', encoding='utf-8-sig')
cols = ['实体A', '关系', '实体B']
df = df[cols].fillna('').astype(str).apply(lambda x: x.str.strip())
df = df[(df != '').all(axis=1)].reset_index(drop=True)
print(f"原始三元组: {len(df)} 条")

# ========= 2. 删除孤立小岛，只保留最大连通子图 =========
G_temp = nx.DiGraph()
G_temp.add_edges_from(df[['实体A', '实体B']].itertuples(index=False))

# 找出最大弱连通子图（把有向图当无向图看，找到主图）
largest_cc = max(nx.weakly_connected_components(G_temp), key=len)
valid_entities = set(largest_cc)

df_filtered = df[
    df['实体A'].isin(valid_entities) & df['实体B'].isin(valid_entities)
].copy()

print(f"删除孤岛后剩余三元组: {len(df_filtered)} 条（删除了 {len(df) - len(df_filtered)} 条）")
print(f"最大连通子图节点数: {len(valid_entities)}")

# ========= 3. 重新构建最终图（节点用数字ID，保证JS定位准确）=========
G = nx.DiGraph()
node_to_id = {}
current_id = 0

for _, row in df_filtered.iterrows():
    a, b, r = row['实体A'], row['实体B'], row['关系']
    
    if a not in node_to_id:
        node_to_id[a] = current_id
        G.add_node(current_id, label=a, title=a)
        current_id += 1
    if b not in node_to_id:
        node_to_id[b] = current_id
        G.add_node(current_id, label=b, title=b)
        current_id += 1
    
    G.add_edge(node_to_id[a], node_to_id[b], label=r, title=r)

print(f"最终图谱 → 节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}")

# ========= 4. PyVis 可视化设置 =========
net = Network(
    height='950px', width='100%', directed=True, bgcolor='#fafafa',
    font_color='black', filter_menu=False, select_menu=False
)
net.from_nx(G)
net.force_atlas_2based(
    gravity=-80, central_gravity=0.015, spring_length=250,
    spring_strength=0.08, damping=0.9, overlap=1
)
net.set_edge_smooth('dynamic')
net.show_buttons(filter_=['physics'])  # 保留右下角调参按钮

# ========= 5. 生成 HTML =========
full_html = net.generate_html()

# ========= 6. 构造供JS使用的JSON数据 =========
entity_map = {label: nid for label, nid in node_to_id.items()}  # "有效应力" → 123
all_relations = sorted(df_filtered['关系'].unique())

entity_json = json.dumps(entity_map, ensure_ascii=False)
relation_json = json.dumps(all_relations, ensure_ascii=False)

# ========= 7. 注入：中文查询面板 + 版权水印 =========
copyright_watermark = """
<div style="position:fixed; bottom:15px; right:20px; background:rgba(0,0,0,0.65); color:white; 
    padding:10px 20px; border-radius:30px; font-family:'Microsoft YaHei',sans-serif; 
    font-size:15px; font-weight:bold; z-index:9999; box-shadow:0 4px 15px rgba(0,0,0,0.3);
    pointer-events:none; border:2px solid rgba(255,255,255,0.3);">
    © 广西民族大学建筑工程学院
</div>
"""

chinese_panel = f"""
<style>
    #kg-panel {{position:absolute; top:15px; left:15px; background:white; padding:18px; border-radius:12px;
        box-shadow:0 6px 25px rgba(0,0,0,0.18); z-index:10000; font-family:'Microsoft YaHei'; min-width:440px;
        border:1px solid #ddd;}}
    #kg-panel select, #kg-panel input, #kg-panel button {{padding:9px 14px; margin:5px 4px; border-radius:6px;
        border:1px solid #ccc; font-size:14px;}}
    #kg-panel button {{background:#3498db; color:white; border:none; cursor:pointer;}}
    #kg-panel button:hover {{background:#2980b9;}}
    #kg-panel button.reset {{background:#95a5a6;}}
    #kg-panel button.reset:hover {{background:#7f8c8d;}}
</style>

<div id="kg-panel">
    <div style="font-weight:bold; font-size:19px; margin-bottom:14px; color:#2c3e50;">
        土力学知识图谱查询系统@广西民族大学建筑工程学院
    </div>
    <div>
        <select id="type">
            <option value="entity">实体（节点）</option>
            <option value="relation">关系（边）</option>
        </select>
        <select id="value"></select>
        <button onclick="locate()">定位</button>
        <button class="reset" onclick="resetView()">重置</button>
    </div>
    <div style="margin-top:12px;">
        <input type="text" id="search" placeholder=" 输入关键词搜索（如：有效应力、固结、摩尔圆）" style="width:100%;">
    </div>
</div>

<script>
const ENTITIES = {entity_json};
const RELATIONS = {relation_json};

const typeSel = document.getElementById('type');
const valSel = document.getElementById('value');

function updateOptions() {{
    valSel.innerHTML = '<option>-- 请选择 --</option>';
    if (typeSel.value === 'entity') {{
        Object.keys(ENTITIES).sort().forEach(l => {{
            let o = document.createElement('option'); o.value = l; o.textContent = l; valSel.appendChild(o);
        }});
    }} else {{
        RELATIONS.forEach(r => {{
            let o = document.createElement('option'); o.value = r; o.textContent = r; valSel.appendChild(o);
        }});
    }}
}}
typeSel.onchange = updateOptions; updateOptions();

window.locate = function() {{
    const v = valSel.value;
    if (!v || v === '-- 请选择 --') return;
    if (typeSel.value === 'entity') {{
        const id = ENTITIES[v];
        const neighbors = network.getConnectedNodes(id);
        network.selectNodes([id, ...neighbors]);
        network.focus(id, {{scale: 2.3, animation: {{duration: 1200}}}});
    }} else {{
        const edges = network.body.data.edges._data;
        const eids = Object.keys(edges).filter(id => edges[id].label === v);
        if (eids.length > 0) {{
            network.selectEdges(eids);
            network.focus(edges[eids[0]].from, {{scale: 1.6, animation: true}});
        }}
    }}
}};

window.resetView = () => network.setSelection({{nodes: [], edges: []}});

document.getElementById('search').addEventListener('keyup', e => {{
    if (e.key === 'Enter') {{
        const q = this.value.trim();
        if (!q) return;
        for (let label in ENTITIES) {{
            if (label.includes(q)) {{
                const id = ENTITIES[label];
                const conn = network.getConnectedNodes(id);
                network.selectNodes([id, ...conn]);
                network.focus(id, {{scale: 2.3, animation: {{duration: 1000}}}});
                return;
            }}
        }}
        alert('未找到：' + q);
    }}
}});
</script>
"""

# 最终注入：水印 + 查询面板
full_html = full_html.replace("</body>", copyright_watermark + chinese_panel + "</body>")

# ========= 8. 保存最终文件 =========
output_file = "土力学知识图谱_广西民族大学正式版.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(full_html)

size_mb = os.path.getsize(output_file) / (1024 * 1024)
print("=" * 90)
print("【土力学知识图谱正式版生成成功！】")
print(f"文件名：{output_file}")
print(f"文件大小：{size_mb:.2f} MB")
print("功能已全部实现：")
print("   ✓ 自动删除孤立小节点")
print("   ✓ 全中文智能查询 + 一键定位")
print("   ✓ 输入框模糊搜索")
print("   ✓ 右下角永久版权水印")
print("   ✓ 布局清晰、响应迅速")
print("直接双击打开，即可用于课堂教学、毕业答辩、论文插图、学院宣传！")
print("=" * 90)
