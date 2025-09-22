# Evaluation Directory - DeepResearch Project

## 概述
Evaluation目录包含DeepResearch项目的基准测试评估脚本和测试基础设施。该系统支持多种权威基准测试，提供自动化的答案评估、性能度量和统计分析功能。

## 支持的基准测试

### 1. HLE (Human-Like Evaluation) 基准
- **文件**: `evaluate_hle_official.py`
- **用途**: 评估模型在类似人类的问答任务中的表现
- **特点**: 使用结构化的答案格式和置信度评分

### 2. DeepSearch 基准
- **文件**: `evaluate_deepsearch_official.py`
- **用途**: 评估深度搜索和信息检索能力
- **支持数据集**:
  - `gaia`: GAIA基准测试
  - `browsecomp_zh`: 中文浏览理解基准
  - `browsecomp_en_full`: 英文浏览理解完整版
  - `webwalker`: WebWalker导航基准
  - `xbench-deepsearch`: X-Bench深度搜索基准

### 3. 专用评估系统
- **文件**: `prompt.py`
- **内容**: 包含所有基准测试的提示词模板和评估标准

## 评估方法论

### 答案提取与评估
1. **答案格式标准化**: 使用`<answer>`标签提取最终答案
2. **LLM裁判系统**: 使用强大的语言模型作为裁判，评估答案正确性
3. **多轮评估**: 支持多次运行以提高评估可靠性

### 评估指标
- **准确率 (Accuracy)**: 答案正确的比例
- **Pass@K**: 在K次尝试中至少正确一次的概率
- **工具使用统计**: 搜索、访问、代码执行等工具的使用情况
- **Token消耗**: 输入和输出的token数量统计
- **成本估算**: 基于token使用量的成本计算

### 统计分析
- **多轮平均**: 多次运行的平均性能
- **最佳表现**: 最佳单轮表现
- **工具效率**: 正确解决问题时的工具使用效率
- **终止条件分析**: 任务完成、最大轮次、最大token限制等

## 数据格式要求

### 输入格式 (JSONL)
```json
{
  "question": "问题内容",
  "answer": "标准答案",
  "prediction": "模型预测答案",
  "records": [{"role": "assistant", "content": "对话记录"}],
  "usage": {"prompt_tokens": 100, "completion_tokens": 200}
}
```

### 输出格式
- **详细评估**: `.eval_details.jsonl` - 包含每个样本的详细评估结果
- **汇总报告**: `.report.json` - 包含整体性能指标和统计数据

## 环境配置

### HLE评估环境变量
```bash
export API_KEY=Your_api_key
export BASE_URL=Your_base_url
```

### 其他基准测试环境变量
```bash
export OPENAI_API_KEY=Your_openai_api_key
export OPENAI_API_BASE=Your_openai_api_base
export API_KEY=Your_api_key
export BASE_URL=Your_base_url
export Qwen2_5_7B_PATH=Your_qwen_model_path
```

## 使用方法

### HLE评估
```bash
python evaluate_hle_official.py \
  --input_fp path/to/input.jsonl \
  --repeat_times 3 \
  --tokenizer_path path/to/tokenizer
```

### DeepSearch评估
```bash
python evaluate_deepsearch_official.py \
  --input_folder path/to/prediction_folder \
  --dataset gaia \
  --restore_result_path summary.jsonl
```

## 评估流程

### 1. 数据预处理
- 加载预测结果文件
- 验证数据格式完整性
- 准备评估环境

### 2. 并行评估
- 使用线程池并行处理多个样本
- 调用LLM裁判进行答案评估
- 处理网络异常和重试机制

### 3. 结果聚合
- 计算整体准确率
- 生成详细统计报告
- 输出可视化指标

### 4. 质量控制
- 答案格式验证
- 异常处理和错误恢复
- 评估结果一致性检查

## 评估裁判系统

### 裁判模型选择
- **GAIA**: Qwen2.5-72B-Instruct
- **BrowseComp**: GPT-4o-2024-08-06
- **X-Bench**: Gemini-2.0-flash-001
- **通用**: 可配置的LLM裁判

### 评估标准
- **语义匹配**: 关注答案的语义正确性，而非字面匹配
- **完整性**: 答案必须包含所有必要信息
- **准确性**: 不能包含错误或矛盾的信息
- **容错性**: 允许合理的格式变化和翻译差异

## 工具使用分析

### 支持的工具类型
- **search**: 网络搜索工具
- **visit**: 网页访问工具
- **PythonInterpreter**: 代码执行工具
- **其他**: 自定义工具

### 统计维度
- 平均工具调用次数
- 工具使用分布
- 正确解决问题的工具效率
- 工具使用与准确率的相关性

## 性能优化

### 并发处理
- 多线程并行评估
- 线程安全的API客户端管理
- 资源使用优化

### 缓存机制
- 评估结果缓存
- 错误重试机制
- 网络请求优化

## 扩展性

### 自定义基准测试
- 通过`prompt.py`添加新的评估提示词
- 配置特定的裁判模型
- 定义专门的评估标准

### 数据集适配
- 支持多种数据格式
- 可配置的答案提取逻辑
- 灵活的评分标准

## 与主系统集成

### 推理系统对接
- 接收来自推理系统的预测结果
- 支持多种输出格式
- 实时评估和反馈

### 实验管理
- 评估结果存储和版本控制
- 实验对比和分析
- 性能趋势监控

## 质量保证

### 评估可靠性
- 多轮评估减少随机性
- 裁判模型的一致性检查
- 异常结果的二次验证

### 结果验证
- 评估结果的交叉验证
- 统计显著性的检验
- 评估标准的定期更新

---

*此文档由DeepResearch项目智能初始化系统生成*
*最后更新: 2025-09-19*