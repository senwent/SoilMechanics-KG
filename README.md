# SoilMechanics-KG
面向土力学教学和科研的交互式知识图谱生成与可视化工具，支持从三元组 CSV 自动构建图谱、去除孤立子图、生成中文查询面板与水印，并导出可直接在浏览器打开的交互式 HTML 演示页。

**SoilKG（土力学知识图谱）** 是一个面向土力学教学与科研的轻量级工具。它能从标准三元组 CSV（列名：`实体A, 关系, 实体B`）自动构建知识图谱，自动剔除孤立子图，生成基于 `pyvis` 的交互式 HTML 演示页面，并内置中文查询面板与版权水印，方便课堂演示、论文插图与院系展示。

---

## 功能亮点
- 自动读取 CSV（`实体A, 关系, 实体B`）并清理数据（去空、去首尾空格）。  
- 自动保留最大弱连通子图（删除孤立小岛），减少噪声。  
- 使用 `networkx` 构图、`pyvis` 渲染交互式 HTML。  
- 内置中文查询面板（按实体/关系定位、模糊搜索回车定位）。  
- 右下角永久版权水印（可自定义或关闭）。  
- 生成的 HTML 可直接离线打开，适合课堂演示与嵌入网页。

---

## 快速开始

1. 克隆仓库并创建虚拟环境（推荐）
```bash
git clone https://github.com/<你的用户名>/soilkg.git
cd soilkg
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
.venv\Scripts\activate       # Windows

2. 安装依赖

pip install -r requirements.txt


3. 准备数据
将 CSV 放在 data/SoilMechanicsMarkDown_sample.csv（或其它路径），CSV 必须包含列：实体A, 关系, 实体B（UTF-8-sig 编码，首行列名一致）。

示例（CSV）：

实体A,关系,实体B
有效应力,影响,孔隙水压力
固结,导致,沉降
摩尔圆,用于,应力分析


4. 运行示例（默认脚本）

python src/soil_kg.py -i data/SoilMechanicsMarkDown_sample.csv -o demos/土力学知识图谱_demo.html


然后在浏览器中打开 demos/土力学知识图谱_demo.html
