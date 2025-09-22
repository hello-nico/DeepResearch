# DeepResearch・LangGraph 集成规划

## 目标

在现有基于 LangGraph 的 Agent 框架中最大化发挥 Tongyi DeepResearch 模型的价值，实现稳定可控的深度检索能力。

## 设计原则

- 引入协议适配层，让 DeepResearch 的 `<tool_call>` / `<answer>` 与 LangGraph 的 `tool_calls` 结构互通。
- 模块化设计：在 planner / executor / reviewer 等节点灵活替换 Tongyi，以评估不同角色的性价比。
- 利用 LangGraph 的状态管理与 DeepResearch 的长上下文、高强度规划互补，确保链路可观测、可回退。

## 集成场景

### 1. Tongyi 作为研究执行体（Search Executor）

- 构建 LangGraph 状态图：Planner → DeepResearch Executor → Synthesizer。
- Planner 拆分复杂问题为多个子任务，逐个调度 DeepResearch `_run` 处理。
- DeepResearch 内部复用搜索、访问网页、学术检索、Python、文件解析等工具（`inference/react_agent.py` 系列工具）。
- 在 LangGraph 节点中捕获 DeepResearch 的 `messages`、计数重试和超时；失败时回滚给 Planner 或切换备用模型。
- 适合“深挖证据 + 撰写报告”场景，可通过 LangGraph 将中间 `<tool_response>` 记录到外部存储供复用。

### 2. Tongyi 作为规划器（Planner）

- 利用 Tongyi Heavy 模式生成详细研究计划：步骤序列、工具选择、产出格式。
- 计划以结构化 JSON 返回，LangGraph 将其映射为节点/边并驱动其他执行器（可使用轻量模型或纯工具）。
- 在执行阶段允许 Tongyi 作为 reviewer 节点，根据实际结果动态调整计划。
- 适用于成本敏感应用：高价值部分由 Tongyi 决策，执行交给低成本资源。

### 3. 复合策略

- 在 Planner 与 Executor 双角色中测试 Tongyi 的组合，例如 Planner（Tongyi）+ Executor（GPT-4o）或 Planner（GPT-4o）+ Executor（Tongyi），比较成本/效果。
- 并行调度：参考 `inference/run_multi_react.py` 在 LangGraph 中并发多个 DeepResearch 实例，进行多路径探索，最后由判别模型筛选最优结论。
- 差错防护：增加 LangGraph Guardrail 节点校验 DeepResearch 输出，包括格式验证、引用链接可用性检查、安全过滤等。

## 适配实现要点

- 编写 `DeepResearchAdapter`（LangGraph `Runnable`）：
  - 输入：LangGraph `messages`。
  - 调用：`MultiTurnReactAgent._run`。
  - 输出：根据 `<tool_call>` 解析 `tool_calls`，并把 `<answer>` 填充为 `AIMessage.content`。
  - 处理 `<tool_response>` 为 `HumanMessage`，保证 LangGraph 能驱动后续工具。
- 对工具返回结构做必要封装，使 LangGraph 节点能消费 DeepResearch 的 JSON 字符串。
- 针对超长对话与多轮工具调用，引入 `max_round`／超时控制以及日志追踪。

## 验证步骤

1. UFO 测试图：Planner（GPT-4o）+ DeepResearch Executor + 总结；验证长链路稳定性。
2. 将 Planner 换成 Tongyi，观测计划质量与执行成本变化。
3. 引入多实例并行与 Reviewer 节点，衡量完成质量、耗时与费用。
4. 记录指标：工具调用次数、平均响应时间、有效引用数量、成功率。

## 后续工作

- 完善文档：在 `AGENTS.md` / `README` 补充新集成流程，提供环境变量、命令示例。
- 建立回归集：收集典型研究任务，定期跑通 LangGraph 集成链路，为模型升级提供基准。
- 探索与外部知识库整合，将 DeepResearch 的中间证据写入可查询存储，增强长周期任务的知识沉淀。
