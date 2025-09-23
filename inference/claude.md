# Inference Directory - DeepResearch Project

## 概述
Inference目录包含DeepResearch项目的核心智能代理实现和工具系统。该系统基于ReAct (Reasoning+Action) 模式，实现了多轮对话代理、工具调用、批量执行等功能，是整个项目的中枢神经系统。

## 核心架构

### 🔥 MultiTurnReactAgent - 多轮对话代理
**位置**: `react_agent.py:1`
- **设计模式**: ReAct (思考→行动→观察)
- **核心特性**:
  - 多轮对话管理和上下文维护
  - 工具调用和结果处理
  - 智能终止条件判断
  - 系统提示词动态管理

### 🚀 BatchExecutionSystem - 批量执行系统
**位置**: `run_multi_react.py:1`
- **并发处理**: 多端口并发执行
- **数据分割**: 自动数据集分割和分配
- **断点续传**: 支持中断后继续执行
- **结果聚合**: 自动收集和合并执行结果

### 🧠 LangGraphExecutor - LangGraph 集成执行器
**位置**: `langgraph_executor.py:1`
- **适配器**: `DeepResearchAdapter` 将 `MultiTurnReactAgent` 的 `<tool_call>`、`<answer>` 转换为 LangGraph `messages`
- **状态图**: `create_deepresearch_executor_graph` 构建 Planner → Executor → Synthesizer 流程
- **默认链路**: 提供 `create_default_planner`、`create_default_synthesizer` 便于快速接入 LLM 规划/汇总
- **日志追踪**: 记录每步工具调用、耗时与执行结果，便于外部观测与回放

### 🧩 DeepResearchNode - 可复用节点封装
**位置**: `deepresearch_node.py:1`
- **封装目标**: 将 Planner → DeepResearch 执行器 → Synthesizer 打包为独立 `Runnable`
- **应用场景**: 可直接嵌入其他 LangGraph 项目，通过 `node.invoke({"question": ...})` 获取答案、计划与任务轨迹
- **默认工厂**: `build_default_deepresearch_node` 读取环境变量自动构建 Planner/Synthesizer/Adapter
- **输出结构**: 返回 `answer`、`plan`、`task_results`、`messages` 及序列化消息，方便日志化处理

### 🛠️ ToolSystem - 工具集成系统
- **搜索工具**: `tool_search.py` - 网络搜索和信息检索；支持 Serper 与 Tavily 自动切换，可通过参数 `provider` 指定
- **访问工具**: `tool_visit.py` - 网页内容访问和解析；增强摘要容错，支持无 LLM 时的降级提取
- **学术工具**: `tool_scholar.py` - 学术论文搜索和引用
- **文件工具**: `tool_file.py` - 文件上传和处理
- **代码工具**: `tool_python.py` - Python代码执行

### 3. 文件处理子模块 (`file_tools/`)

#### SingleFileParser (`file_parser.py`)
- **功能**: 单文件解析器
- **支持格式**: 文档、表格、压缩包、音视频
- **特性**: 自动格式检测和解析

#### VideoAgent (`video_agent.py`)
- **功能**: 视频内容分析代理
- **支持格式**: MP4, MOV, AVI, MKV, WebM
- **特性**: 视频内容提取和总结

#### VideoAnalysis (`video_analysis.py`)
- **功能**: 视频深度分析
- **特性**: 帧级别分析、内容理解

#### Utils (`utils.py`)
- **功能**: 通用工具函数
- **包含**: 文本处理、格式转换等

#### IDP (`idp.py`)
- **功能**: 智能文档处理
- **特性**: 结构化信息提取

### 4. 提示系统 (`prompt.py`)

#### SYSTEM_PROMPT
- **功能**: 系统级提示词
- **内容**:
  - 代理角色定义
  - 工具使用说明
  - 输出格式要求
  - 当前日期注入

#### EXTRACTOR_PROMPT
- **功能**: 网页/文件内容提取提示
- **结构**:
  - Rational: 相关性分析
  - Evidence: 关键信息提取
  - Summary: 内容总结

### 5. 评估数据 (`eval_data/`)

#### 数据格式
- **example.jsonl**: 基础问题-答案对
- **example_with_file.jsonl**: 包含文件附件的问题
- **file_corpus/**: 文件语料库

#### 数据结构
```json
{
  "question": "用户问题",
  "answer": "标准答案",
  "messages": [
    {"role": "system", "content": "系统提示"},
    {"role": "user", "content": "用户输入"}
  ]
}
```

## 执行流程

### 1. 代理执行流程
1. **初始化**: 加载工具、配置LLM
2. **问题处理**: 提取用户问题
3. **多轮推理**:
   - LLM生成思考或工具调用
   - 执行工具并获取结果
   - 将结果加入上下文
4. **终止条件**:
   - 生成答案（`<answer>`标签）
   - 达到最大轮次（`max_rounds` 可通过 LangGraph 适配器或直接传参控制）
   - 上下文超限
   - 超时（默认 150 分钟，可通过 `max_runtime_seconds` 自定义）

### 2. 工具调用机制
```python
# 工具调用格式

{"name": "tool_name", "arguments": {"param": "value"}}
<code>
# Python代码内容
</code>
```

### 3. 批量执行流程
1. **数据加载**: 从JSONL文件加载评估数据
2. **数据分割**: 支持数据集分割和并行处理
3. **端口分配**: 为每个问题分配固定端口（sticky assignment）
4. **并发执行**: 使用线程池并发处理多个问题
5. **结果收集**: 收集并保存结果到JSONL文件

## 关键配置

### 环境变量
- `MAX_LLM_CALL_PER_RUN`: 最大LLM调用次数（默认100）
- `VISIT_SERVER_TIMEOUT`: 网页访问超时（默认200s）
- `WEBCONTENT_MAXLENGTH`: 网页内容最大长度（默认150K）
- `JINA_API_KEYS`: Jina服务API密钥
- `SERPER_KEY_ID`: Serper搜索API密钥
- `SANDBOX_FUSION_ENDPOINT`: Python沙箱端点

### 模型配置
```python
llm_cfg = {
    'model': 'model_path',
    'generate_cfg': {
        'max_input_tokens': 320000,
        'max_retries': 10,
        'temperature': 0.6,
        'top_p': 0.95,
        'presence_penalty': 1.1
    }
}
```

## 依赖关系

### 核心依赖
- **Qwen Agent**: 代理框架基础
- **OpenAI API**: LLM调用接口
- **Transformers**: 模型和分词器
- **Requests**: HTTP请求
- **Tiktoken**: Token计数

### 外部服务
- **Serper API**: Google搜索和学术搜索
- **Jina Reader**: 网页内容提取
- **Sandbox Fusion**: Python代码执行沙箱

## 扩展指南

### 1. 添加新工具
1. 继承 `BaseTool` 类
2. 实现 `call` 方法
3. 在 `react_agent.py` 中注册
4. 更新 `SYSTEM_PROMPT` 中的工具描述

### 2. 修改执行流程
- 修改 `MultiTurnReactAgent._run` 方法
- 调整终止条件和轮次限制
- 更新工具调用逻辑

### 3. 扩展文件格式支持
- 在 `file_tools/file_parser.py` 中添加新的解析器
- 更新 `FileParser` 类的支持格式列表

## 错误处理机制

### 1. 网络错误
- 搜索服务重试（最多5次）
- 网页访问重试（最多8次）
- 指数退避策略

### 2. 工具执行错误
- JSON格式验证
- 参数验证
- 超时处理
- 错误信息返回

### 3. 系统级错误
- 上下文长度管理
- 内存溢出保护
- 进程超时控制

## 性能优化

### 1. 并发处理
- 多线程执行（`ThreadPoolExecutor`）
- 端口负载均衡
- 数据分割处理

### 2. 内存管理
- 上下文截断
- 内容压缩
- Token数量监控

### 3. 缓存策略
- 问题到端口映射缓存
- 工具结果缓存（可选）

## 监控和调试

### 1. 日志输出
- 轮次信息打印
- 工具调用结果
- 错误信息记录

### 2. 中间结果
- 每轮对话保存
- 工具执行结果记录
- 最终答案生成

### 3. 性能指标
- Token使用量统计
- 执行时间记录
- 成功率计算
