# WebAgent 深度研究代理家族

## 项目概述

WebAgent是DeepResearch项目中的一个核心模块，由阿里巴巴通义实验室开发的一系列专注于网络信息搜索和处理的智能代理组成。这个家族包含多个子项目，每个项目都有其特定的功能和目标，共同构建了一个完整的深度研究生态系统。

## 子项目架构

### 1. WebDancer (Web舞者) - 自主信息搜索代理
**定位**: 原生代理搜索模型，朝着自主信息搜索代理和类DeepResearch模型发展
**论文**: [WebDancer: Towards Autonomous Information Seeking Agency](https://arxiv.org/pdf/2505.22648)
**模型**: WebDancer-32B (32K上下文)

**核心特性**:
- 使用ReAct框架的原生代理搜索推理模型
- 四阶段训练范式：浏览数据构建、轨迹采样、监督微调、强化学习
- 数据中心方法结合轨迹级监督微调和强化学习(DAPO)
- 在GAIA上达到64.1%的Pass@3分数，在WebWalkerQA上达到62.0%

**架构组件**:
- `/demos/agents/search_agent.py`: 基于Qwen Agent的搜索代理实现
- `/demos/tools/private/`: 私有搜索和访问工具
- `/demos/gui/`: Gradio Web界面
- `/demos/llm/`: LLM集成层(支持OpenAI和通义千问)

### 2. WebSailor (Web水手) - 超人推理导航代理
**定位**: 专注于复杂推理任务的Web代理，支持多轮ReAct对话
**论文**: [WebSailor: Navigating Super-human Reasoning for Web Agent](https://arxiv.org/pdf/2507.02592)
**模型**: WebSailor-3B/7B/32B (32K上下文)

**核心特性**:
- 完整的后训练方法论，支持扩展思考和复杂任务
- SailorFog-QA: 高不确定性和难度的QA基准
- 有效的后训练流水线：RFT冷启动 + DUPO(复制采样策略优化)
- 在BrowseComp-en上达到12.0%，BrowseComp-zh上达到30.1%，GAIA上达到55.4%

**架构组件**:
- `/src/react_agent.py`: 多轮ReAct代理实现
- `/src/tool_search.py`: 批量网络搜索工具
- `/src/tool_visit.py`: 网页访问和内容提取工具
- `/src/prompt.py`: 系统提示和评估模板

### 3. WebWalker (Web漫步者) - 网络遍历基准
**定位**: LLM在网络遍历中的基准测试和多代理框架
**论文**: [WebWalker: Benchmarking LLMs in Web Traversal](https://arxiv.org/pdf/2501.07572)
**发表**: ACL 2025

**核心特性**:
- ReAct格式的探索代理
- 信息提取和批判性评估系统
- 记忆管理和多步推理
- WebWalkerQA基准测试

**架构组件**:
- `/src/agent.py`: WebWalker代理核心实现
- `/src/rag_system.py`: RAG系统集成
- `/src/prompts.py`: 系统提示模板
- `/src/evaluate.py`: 评估框架

### 4. WebShaper (Web塑造者) - 数据合成代理
**定位**: 通过信息搜索形式化进行代理式数据合成
**论文**: [WebShaper: Agentically Data Synthesizing via Information-Seeking Formalization](https://arxiv.org/pdf/2507.15061)
**模型**: WebShaper-32B (32K上下文)

**核心特性**:
- 基于任务形式化的数据合成方法
- 代理式Expander迭代生成和验证问题
- 在GAIA上达到60.19，WebWalkerQA上达到52.50

### 5. WebWatcher (Web观察者) - 视觉语言深度研究代理
**定位**: 突破视觉语言深度研究代理的新前沿
**论文**: [WebWatcher: Breaking New Frontier of Vision-Language Deep Research Agent](https://arxiv.org/pdf/2508.05748)
**模型**: WebWatcher-7B/32B (32K上下文)

**核心特性**:
- 多工具支持：搜索/访问/图像搜索/代码解释器
- 视觉语言理解能力
- 复杂VQA问题解决

### 6. 其他项目
- **WebResearcher**: 研究代理 (论文阶段)
- **WebResummer**: 内容摘要代理 (论文阶段)
- **WebWeaver**: 信息编织代理 (论文阶段)
- **WebSailor-V2**: WebSailor的升级版本

## 共享架构模式

### 核心技术栈
所有WebAgent项目都基于以下技术栈：

1. **Qwen Agent框架**:
   - 统一的代理基类 (Assistant/FnCallAgent)
   - 工具注册和管理机制
   - 消息处理和对话管理

2. **工具生态**:
   - **Search工具**: 基于Google Serper的批量搜索
   - **Visit工具**: 基于Jina Reader的网页内容提取
   - **多线程处理**: 支持并发工具调用

3. **LLM集成**:
   - OpenAI API兼容接口
   - 通义千问API集成
   - SGLang/vLLM本地部署支持

### 通用设计模式

#### 1. 代理架构模式
```python
class SearchAgent(Assistant):
    def __init__(self, function_list, llm, system_message, **kwargs):
        super().__init__(function_list, llm, system_message, **kwargs)

    def _run(self, messages, **kwargs):
        # 工具调用循环
        while num_llm_calls_available > 0:
            # LLM推理
            # 工具检测和调用
            # 结果处理和记忆更新
```

#### 2. 工具注册模式
```python
@register_tool("search", allow_overwrite=True)
class Search(BaseTool):
    name = "search"
    description = "工具描述"
    parameters = {"type": "object", "properties": {...}}

    def call(self, params, **kwargs):
        # 工具实现逻辑
```

#### 3. 提示工程模式
- 系统提示定义代理角色和能力
- 用户提示模板化工具调用格式
- 评估提示标准化答案质量判断

### 数据流和集成模式

#### 工具调用流程
1. **代理推理**: LLM分析任务并决定工具调用
2. **工具执行**: 并发或顺序执行搜索/访问工具
3. **内容处理**: 提取、摘要、验证信息
4. **记忆管理**: 累积和评估信息相关性
5. **决策制定**: 基于累积信息做出最终判断

#### 多代理协作
- **代理链**: 代理之间的顺序协作
- **代理并行**: 多代理同时处理不同方面
- **专家代理**: 专门化代理处理特定任务

## 与DeepResearch主项目的关系

### 技术演进
- **WebAgent**: 为DeepResearch提供基础代理架构和工具生态
- **DeepResearch**: 基于WebAgent技术栈的端到端深度研究解决方案
- **模型继承**: Tongyi DeepResearch-30B-A3B继承了WebAgent的训练范式

### 生态整合
- **Agent目录**: 包含AgentFounder和AgentScaler，与WebAgent形成完整生态
- **推理系统**: `/inference`目录提供统一的模型推理接口
- **评估框架**: `/evaluation`目录提供标准化的评估方法

### 共享组件
- **工具库**: 搜索、访问、处理工具的标准化实现
- **训练数据**: 共享的代理交互和轨迹数据
- **评估基准**: GAIA、WebWalkerQA、BrowserComp等标准测试集

## 开发指南

### 环境配置
```bash
# 基础依赖
conda create -n webagent python=3.12
pip install -r requirements.txt

# 核心依赖
sglang[all]
qwen-agent[gui,rag,code_interpreter,mcp]
```

### API密钥配置
- `GOOGLE_SEARCH_KEY`: Google Serper搜索API
- `JINA_API_KEY`: Jina Reader网页提取API
- `DASHSCOPE_API_KEY`: 通义千问LLM API

### 模型部署
```bash
# 使用SGLang部署
cd scripts
bash deploy_model.sh MODEL_PATH

# 运行演示
bash run_demo.sh
```

### 扩展开发
1. **新工具开发**: 继承BaseTool类并实现call方法
2. **新代理开发**: 继承Assistant或FnCallAgent类
3. **提示工程**: 在prompt.py中定义系统提示模板
4. **评估集成**: 实现标准化评估接口

## 性能基准

### 主流模型性能对比
| 模型 | 发布时间 | 上下文长度 | 工具列表 |
|------|----------|------------|----------|
| WebDancer-32B | 2025.06.23 | 32K | Search/Visit |
| WebSailor-3B | 2025.07.11 | 32K | Search/Visit |
| WebSailor-7B | 2025.08.06 | 32K | Search/Visit |
| WebSailor-32B | 2025.08.26 | 32K | Search/Visit |
| WebWatcher-7B | 2025.08.27 | 32K | Search/Visit/ImageSearch/CodeInterpreter |
| WebWatcher-32B | 2025.08.27 | 32K | Search/Visit/ImageSearch/CodeInterpreter |
| WebShaper-32B | 2025.08.28 | 32K | Search/Visit |

### 基准测试结果
- **GAIA**: WebShaper-32B达到60.19
- **WebWalkerQA**: WebShaper-32B达到52.50
- **BrowseComp-en**: WebSailor-72B达到12.0%
- **BrowseComp-zh**: WebSailor-72B达到30.1%

## 贡献指南

### 代码结构
- `/项目名称/demos/`: 演示和示例代码
- `/项目名称/src/`: 核心实现代码
- `/项目名称/dataset/`: 数据集和基准
- `/项目名称/scripts/`: 部署和运行脚本

### 开发规范
- 遵循Qwen Agent框架的设计模式
- 实现标准化的工具注册接口
- 提供完整的类型注解和文档
- 实现可复现的评估结果

## 联系信息

- **项目主页**: https://github.com/Alibaba-NLP/WebAgent
- **HuggingFace**: https://huggingface.co/Alibaba-NLP
- **ModelScope**: https://modelscope.cn/organizations/WebAgent
- **联系邮箱**: yongjiang.jy@alibaba-inc.com

---

**注意**: WebAgent项目正在快速发展中，更多功能和模型即将发布。欢迎关注项目的最新动态和贡献代码！