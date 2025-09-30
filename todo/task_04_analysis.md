# Task 04：工具调用次数上限需求可行性分析

## 背景概述
- 现有 `refactor/tongyi_ds` 目录基于原 `tongyi-ds` 进行 LangGraph 化改造，当前需求希望在运行期除了 `max_llm_calls` 之外，再加入一个 `max_requests` 参数，用于限制外部工具被调用的次数；一旦达到 `max_llm_calls` 或 `max_requests` 其中任一阈值，就提前结束流程并返回结果。需求来源参见任务描述。【F:todo/task_04_req.md†L1-L7】

## 现有流程梳理
1. **配置与状态**：`AgentRuntimeConfig` 目前仅包含 `max_llm_calls` 等参数；初始状态在 `build_initial_state` 中写入 `llm_calls_remaining`，没有针对工具调用的计数。【F:refactor/tongyi_ds/config.py†L33-L55】【F:refactor/tongyi_ds/state.py†L31-L66】
2. **图构建**：`build_tongyi_deepresearch_graph` 通过 `StateGraph` 串联 `LLMNode`、`ToolNode` 与 `FinalizeNode`，最终在 `run_tongyi_deepresearch` 中设置递归深度与初始状态，未额外限制工具节点的执行次数。【F:refactor/tongyi_ds/graph.py†L1-L82】
3. **LLM 节点**：`LLMNode` 会在每轮检查 `max_llm_calls`、超时与 token 上限，若触发则通过 `_limit_reached` 返回终止状态；但这里并未统计工具请求次数，也没有对应的元数据字段。【F:refactor/tongyi_ds/llm_node.py†L21-L161】
4. **工具节点**：`ToolNode` 调用 `ToolInvoker.invoke` 执行工具，返回结果给状态，但同样没有计数或限制逻辑。【F:refactor/tongyi_ds/tool_node.py†L1-L39】【F:refactor/tongyi_ds/tool_runtime.py†L1-L44】

## 可行性结论
- **可行**：需求与现有架构兼容。当前 LangGraph 工作流在状态中维护了消息、轮次等信息，只需拓展状态字典与配置，即可记录并限制工具调用次数，不会破坏节点之间的数据格式约定。
- **风险可控**：需要关注与递归深度 `recursion_limit` 的关系；该值按 `max_llm_calls` 推导，为避免工具节点在限制变小后导致多余的递归，可在计算时取两者的上界或添加安全系数即可。

## 实施建议
1. **扩展配置**：在 `AgentRuntimeConfig` 新增 `max_tool_calls`（默认值可与 `max_llm_calls` 相同或来自 `MAX_TOOL_CALL_PER_RUN` 环境变量），并在 `GraphBuildConfig.copy_with` 等处保持透传。【F:refactor/tongyi_ds/config.py†L33-L55】
2. **状态初始化**：`build_initial_state` 中新增 `tool_calls_remaining` 字段，初始值为 `max_tool_calls`，并在 `AgentState` 类型中加入 `tool_calls_used` 计数。【F:refactor/tongyi_ds/state.py†L9-L66】
3. **工具节点计数**：在 `ToolNode.__call__` 内部（或 `ToolInvoker.invoke`）更新状态：
   - 读取与递增 `tool_calls_used`。
   - 更新 `metadata["tool_calls_remaining"]`，并在达到上限时设置 `termination` 与提示消息，使下游 `LLMNode` 能感知终止条件。【F:refactor/tongyi_ds/tool_node.py†L1-L39】
4. **LLM 节点终止处理**：`LLMNode.__call__` 在接收来自工具节点的状态时检查 `termination`，必要时直接走 `_limit_reached` 或自定义处理；同时 `_limit_reached` 可添加 `max_tool_calls` 的说明文本。【F:refactor/tongyi_ds/llm_node.py†L21-L161】
5. **递归深度调整**：`run_tongyi_deepresearch` 计算 `recursion_limit` 时综合考虑两种上限，比如 `max(2 * (max_llm_calls + max_tool_calls) + 10, 50)`，避免 LangGraph 提前抛出递归限制错误。【F:refactor/tongyi_ds/graph.py†L59-L82】
6. **配置入口与文档**：若外部 CLI 或配置文件依赖 `GraphBuildConfig`，需同步暴露参数；更新相关 README/配置说明，确保使用者知晓新的限制选项。
7. **测试验证**：在 `refactor/tests/tongyi_ds/test_langgraph_agent.py` 新增覆盖用例，分别验证：
   - 工具调用次数未超过上限时流程正常。
   - 达到上限时提前终止，并返回预期的 `termination` 标记与提示消息。【F:refactor/tests/tongyi_ds/test_langgraph_agent.py†L1-L110】

## 时间与工作量预估
- **开发**：约 0.5~1 天，包含参数扩展、状态更新、终止逻辑与递归限值调整。
- **测试与验证**：约 0.5 天，包括单元测试补充与实际运行一次长链路场景，观察工具调用次数控制情况。

## 额外建议
- 在日志中打印当前的工具调用计数与剩余额度，便于运维诊断。
- 若未来需要对不同工具设置独立限额，可将上述实现抽象为按工具名维护的计数表，但当前需求下全局上限已经足够。
