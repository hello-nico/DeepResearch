# Project: DeepResearch - 通义深度研究智能代理系统

## 概述
DeepResearch 是由阿里巴巴通义实验室开发的智能代理大语言模型，拥有305亿总参数，每个token仅激活33亿参数。该系统专门设计用于**长期深度信息搜索**任务，在多个智能搜索基准测试中展现出最先进的性能。

## 核心特性

### 📊 项目架构
- **模型规模**: 30B-A3B (305亿总参数，33亿激活参数)
- **上下文长度**: 128K tokens
- **推理模式**: ReAct 模式和 IterResearch "Heavy" 模式
- **训练方法**: 持续预训练 + 监督微调 + 强化学习

### 🛠️ 技术栈
- **主要语言**: Python 3.10.0
- **深度学习框架**: PyTorch 2.7.1
- **AI/ML库**: Transformers, vLLM, HuggingFace Hub
- **云服务**: 阿里云服务集成 (DashScope, ModelScope)
- **工具集成**: 搜索、文件解析、代码执行、网页访问

### 🔧 核心依赖
```bash
# 深度学习
torch==2.7.1, transformers==4.56.1, vllm==0.10.1

# AI服务
openai==1.99.5, litellm==1.77.1, dashscope==1.24.4

# Web和数据
aiohttp==3.12.15, beautifulsoup4 (via lxml), pandas==2.3.2

# 工具库
qwen-agent==0.0.26, ray==2.49.1, fastapi==0.116.1
```

## 目录结构
```
DeepResearch/
├── 📁 inference/              # 推理系统和代理实现 → ./inference/claude.md
│   ├── react_agent.py        # ReAct 代理核心实现
│   ├── run_multi_react.py    # 多代理运行系统
│   ├── 📁 file_tools/        # 文件处理工具集
│   ├── 📁 eval_data/         # 评估数据存放
│   └── tool_*.py             # 各种工具实现
├── 📁 evaluation/            # 评估脚本和基准测试 → ./evaluation/claude.md
│   ├── evaluate_*.py         # 各类数据集评估
│   └── prompt.py             # 评估提示词
├── 📁 WebAgent/              # Web代理相关项目 → ./WebAgent/claude.md
│   ├── WebDancer/            # Web信息搜索代理
│   ├── WebSailor/            # Web导航推理代理
│   ├── WebWalker/            # Web遍历基准代理
│   └── WebShaper/            # Web信息结构化代理
├── 📁 Agent/                 # 代理相关组件 → ./Agent/claude.md
├── 📁 assets/                # 项目资源文件
├── requirements.txt          # 主依赖文件
└── README.md               # 项目文档
```

## 关键入口点

### 🔥 核心推理系统
- **主推理入口**: `inference/react_agent.py:1` - ReAct代理实现
- **多代理系统**: `inference/run_multi_react.py:1` - 并行代理执行
- **模型服务**: 通过vLLM和Transformers集成
- **工具调用**: 各种tool_*.py文件实现具体功能

### 📊 评估系统
- **HLE评估**: `evaluation/evaluate_hle_official.py`
- **深度搜索评估**: `evaluation/evaluate_deepsearch_official.py`
- **提示词管理**: `evaluation/prompt.py`

### 🌐 Web代理家族
- **WebDancer**: 自主信息搜索代理
- **WebSailor**: 超人类推理导航代理
- **WebWalker**: Web遍历基准测试代理
- **WebShaper**: 信息结构化代理

## 开发工作流

### 🚀 快速开始
1. **环境设置**: 创建conda环境，Python 3.10.0
2. **依赖安装**: `pip install -r requirements.txt`
3. **数据准备**: 在`eval_data/`中准备JSONL格式QA数据
4. **配置脚本**: 修改`run_react_infer.sh`中的模型路径和API密钥
5. **运行推理**: `bash run_react_infer.sh`

### 🧪 测试和评估
- 使用evaluation目录中的脚本进行基准测试
- 支持多种数据集的自动评估
- 提供性能指标和分析报告

### 🔧 代理开发
- 基于ReAct模式构建智能代理
- 支持工具调用和复杂任务分解
- 集成搜索、计算、文件处理等多种能力

## 导航索引

### 🎯 核心功能区域
- **代理系统**: `inference/` - 智能代理核心实现 → [详细文档](./inference/claude.md)
- **工具集成**: `inference/tool_*.py` - 各种工具能力 → [工具系统](./inference/claude.md#️-toolsystem---工具集成系统)
- **Web代理**: `WebAgent/` - Web相关代理实现 → [WebAgent家族](./WebAgent/claude.md)
- **评估体系**: `evaluation/` - 性能评估和基准测试 → [评估系统](./evaluation/claude.md)
- **代理训练**: `Agent/` - 智能代理训练组件 → [代理组件](./Agent/claude.md)

### 📈 关键模式
- **ReAct推理**: 观察→思考→行动的循环模式 → [推理实现](./inference/claude.md#-multiturnreactagent---多轮对话代理)
- **工具调用**: 通过function calling实现外部工具集成 → [工具调用机制](./inference/claude.md#-工具调用机制)
- **多代理协作**: 并行执行多个代理任务 → [批量执行](./inference/claude.md#-batchexecutionsystem---批量执行系统)
- **持续学习**: 基于合成数据的预训练和微调 → [AgentFounder](./Agent/claude.md#agentfounder---持续预训练代理)

### 🔍 常见任务定位
- **模型推理**: 查看 `inference/react_agent.py` → [详细文档](./inference/claude.md#️-multiturnreactagent---多轮对话代理)
- **搜索功能**: 查看 `inference/tool_search.py` → [搜索工具](./inference/claude.md#搜索工具-tool_searchpy)
- **文件处理**: 查看 `inference/file_tools/` → [文件处理](./inference/claude.md#-filetools---文件处理子模块)
- **评估测试**: 查看 `evaluation/` 目录 → [评估指南](./evaluation/claude.md#使用方法)
- **Web代理**: 查看 `WebAgent/` 各子项目 → [WebAgent项目](./WebAgent/claude.md#-webagent家族概览)

### 🔗 交叉引用地图

#### 架构关系图
```
DeepResearch (主项目)
├── 📊 Agent/ (训练组件)
│   ├── AgentFounder → 持续预训练数据 → inference/
│   └── AgentScaler → 环境扩展能力 → WebAgent/
├── 🚀 inference/ (推理系统)
│   ├── react_agent.py ← 核心ReAct代理
│   ├── tool_*.py ← 工具实现
│   └── file_tools/ ← 文件处理
├── 🌐 WebAgent/ (Web代理家族)
│   ├── WebDancer → 信息搜索
│   ├── WebSailor → 导航推理
│   ├── WebWalker → 遍历基准
│   └── [其他6个专业代理]
└── 📈 evaluation/ (评估体系)
    ├── 基准测试 ← 测试所有组件
    └── 性能分析 ← 优化反馈
```

#### 技术依赖关系
- **基础架构**: Qwen Agent框架 → 所有代理项目
- **工具生态**: 搜索/访问/处理工具 → 跨项目共享
- **评估标准**: GAIA/WebWalkerQA/BrowserComp → 统一评估
- **模型训练**: AgentFounder + AgentScaler → 模型能力提升

#### 数据流向
1. **训练数据**: Agent/ → 生成训练数据 → 模型训练
2. **推理执行**: inference/ → 加载训练模型 → 执行任务
3. **Web交互**: WebAgent/ → 使用推理系统 → Web任务执行
4. **性能评估**: evaluation/ → 评估所有组件 → 反馈优化

### 🎯 问题解决路径

#### 需要实现新的代理功能？
1. **基础能力**: 查看 `inference/claude.md` 了解核心架构
2. **Web特定功能**: 参考 `WebAgent/claude.md` 中的现有实现
3. **训练数据**: 利用 `Agent/claude.md` 中的训练方法
4. **评估验证**: 使用 `evaluation/claude.md` 进行测试

#### 需要优化现有功能？
1. **性能问题**: 查看 `evaluation/claude.md` 的性能指标
2. **架构改进**: 参考 `inference/claude.md` 的架构设计
3. **功能扩展**: 基于 `WebAgent/claude.md` 的成功案例
4. **训练提升**: 利用 `Agent/claude.md` 的训练技术

#### 需要添加新工具？
1. **工具接口**: 参考 `inference/claude.md` 的工具系统
2. **实现示例**: 查看 `WebAgent/claude.md` 的工具实现
3. **集成测试**: 使用 `evaluation/claude.md` 进行验证
4. **性能优化**: 参考 `Agent/claude.md` 的优化方法

### 🚀 快速开始指南

#### 新开发者入门路径
1. **项目概览**: 阅读 `claude.md` (本文档)
2. **核心系统**: 查看 `inference/claude.md`
3. **Web能力**: 浏览 `WebAgent/claude.md`
4. **训练方法**: 了解 `Agent/claude.md`
5. **评估标准**: 参考 `evaluation/claude.md`

#### 特定任务开发路径
- **搜索代理**: `WebAgent/WebDancer/` + `inference/tool_search.py`
- **导航代理**: `WebAgent/WebSailor/` + `inference/tool_visit.py`
- **研究代理**: `inference/react_agent.py` + `Agent/AgentFounder/`
- **评估系统**: `evaluation/` + 所有组件的测试接口

## 性能考虑

### ⚡ 优化要点
- 使用vLLM进行高性能推理
- 支持GPU加速和分布式计算
- 实现了token级别的策略梯度优化
- 采用选择性过滤负样本以稳定训练

### 🎯 模型能力
- 长上下文理解 (128K tokens)
- 复杂推理和任务分解
- 多模态信息处理
- 实时信息搜索和整合

## 相关论文和研究

### 📚 学术成果
该项目包含多个相关研究成果，涵盖了Web代理的各个方面：
- WebWalker: Web遍历基准测试
- WebDancer: 自主信息搜索代理
- WebSailor: 超人类推理导航
- WebShaper: 信息结构化处理
- WebResearcher: 无界推理能力

### 🔬 研究方向
- Web智能代理
- 搜索代理
- 代理强化学习
- 多代理系统
- 代理RAG系统

---

*此文档由DeepResearch项目智能初始化系统生成*
*最后更新: 2025-09-19*