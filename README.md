# 📄 智能简历分析系统 — AI Resume Analyzer

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal?logo=fastapi)](https://fastapi.tiangolo.com)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-ff6384?logo=chartdotjs)](https://www.chartjs.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**AI驱动的简历智能分析工具** — 上传简历即可获得多维评分、技能雷达图、岗位匹配度、针对性改进建议。帮助求职者用数据看懂自己的简历竞争力。

## ✨ 功能亮点

| 功能 | 描述 |
|------|------|
| 📤 **多格式解析** | 支持 PDF / DOCX / TXT 文件上传或直接粘贴文本 |
| 📊 **多维评分** | 完整度(30分) · 技能(25分) · 经验(25分) · 格式(20分)，总计100分+等级评定 |
| 🎯 **岗位匹配** | 5大热门岗位模板，智能关键词匹配，必备技能缺口分析 |
| 📈 **可视化报告** | Chart.js雷达图、技能分类柱状图、分布标签 |
| 💡 **AI改进建议** | 10+条专业建议库，按优先级(高/中/低)排列 |
| 📋 **一键示例** | 内置示例简历，可快速体验完整分析流程 |

## 🏗️ 技术架构

```
┌──────────────────────────────────────────────┐
│                  Frontend                    │
│  HTML5 + CSS3 + Vanilla JS                  │
│  Chart.js 雷达图  · 拖拽上传  · 响应式UI     │
├──────────────────────────────────────────────┤
│                  Backend                     │
│  FastAPI (Python)                           │
│  ├── /api/analyze   简历上传 + 多维分析      │
│  ├── /api/jobs      岗位模板列表             │
│  ├── /api/match     简历 vs 岗位匹配         │
│  └── /api/sample    示例简历                 │
├──────────────────────────────────────────────┤
│               AI Analyzer Engine             │
│  文本解析 → 实体抽取 → 多维评分 → 建议生成    │
│  PyPDF2 / python-docx 文件解析               │
│  技能词库(100+)、岗位模板(5类)、建议库(10+)   │
└──────────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求
- Python 3.10+
- pip

### 安装运行

```bash
cd smart-resume-analyzer
pip install -r requirements.txt
python main.py
```

浏览器打开 [http://localhost:8081](http://localhost:8081)，点击「加载示例简历」即可体验。

## 📁 项目结构

```
smart-resume-analyzer/
├── main.py              # FastAPI 应用入口 + 文件处理
├── analyzer.py          # AI分析引擎（解析、评分、匹配、建议）
├── requirements.txt     # Python依赖
├── static/
│   ├── index.html       # 前端界面（上传区+结果面板）
│   ├── style.css        # 样式（评分卡片+图表布局）
│   └── app.js           # 前端逻辑（Chart.js+拖拽上传）
└── README.md
```

## 🎯 简历展示要点

- **AI应用能力**: 自建简历分析引擎，实体抽取+多维评分算法
- **数据处理**: PDF/DOCX/TXT多格式文件解析
- **算法设计**: TF-IDF关键词匹配、技能分类、岗位匹配算法
- **可视化**: Chart.js雷达图+柱状图，直观展示分析结果
- **产品思维**: 从用户痛点出发（简历写得好不好？），给出可落地的改进建议

## 📝 License

MIT © 2024
