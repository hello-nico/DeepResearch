# DeepResearch 示例

本目录包含DeepResearch的使用示例和演示代码。

## 文件说明

### `deep_research_demo.py`
主要的演示程序，展示了DeepResearch的核心功能和使用方法。

### `simple_usage_example.py`
简化的使用示例，展示基本的DeepResearch调用方式。

### `custom_tools_example.py`
展示如何扩展和自定义工具的示例。

### `langgraph_executor_demo.py`
展示 Planner → DeepResearch Executor → Synthesizer 的 LangGraph 集成流程。

## 快速开始

### 1. 环境准备

确保已安装必要的依赖：

```bash
pip install -r ../requirements.txt
```

### 2. 设置环境变量

创建 `.env` 文件或设置以下环境变量：

```bash
export SERPER_KEY_ID="your_serper_api_key"
export JINA_API_KEYS="your_jina_api_keys"
```

### 3. 运行演示

#### 交互式演示
```bash
python examples/deep_research_demo.py
```

#### 批量演示
```bash
python examples/simple_usage_example.py
```

## 核心功能展示

### 1. 多轮对话推理
DeepResearch采用ReAct模式，通过多轮对话进行深度推理和研究。

### 2. 工具集成
集成了多种研究工具：
- **search**: Google搜索
- **visit**: 网页访问和内容提取
- **google_scholar**: 学术论文搜索
- **PythonInterpreter**: 代码执行和数据分析
- **parse_file**: 文件解析（PDF、DOCX等）

### 3. 智能终止
当Agent收集到足够信息或达到限制时会自动终止并给出答案。

## 使用场景

### 学术研究
```python
# 搜索学术论文
question = "查找关于量子计算在密码学中应用的最新研究"
```

### 商业分析
```python
# 分析公司表现
question = "研究特斯拉2024年的财务表现和市场战略"
```

### 技术调研
```python
# 技术栈分析
question = "分析Python机器学习库的最新特性"
```

### 数据分析
```python
# 数据处理和分析
question = "分析并比较不同机器学习算法的性能"
```

## 自定义扩展

### 添加新工具
```python
from qwen_agent.tools.base import BaseTool, register_tool

@register_tool("custom_tool")
class CustomTool(BaseTool):
    name = "custom_tool"
    description = "自定义工具描述"

    def call(self, params):
        # 工具实现逻辑
        return result
```

### 修改提示词
编辑 `inference/prompt.py` 中的系统提示词来调整Agent行为。

## 注意事项

1. **API限制**: 某些工具需要API密钥，请确保正确设置
2. **网络依赖**: 搜索和网页访问功能需要网络连接
3. **模型要求**: 需要兼容的模型文件支持
4. **资源消耗**: 深度研究可能消耗较多计算资源

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查API密钥是否正确
   - 确认网络连接正常

2. **模型加载失败**
   - 检查模型路径是否正确
   - 确认有足够的内存和存储空间

3. **工具执行失败**
   - 检查工具参数格式
   - 查看详细错误日志

### 调试模式

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 贡献

欢迎提交问题报告和改进建议。请参考主项目的贡献指南。

## 许可证

遵循主项目的许可证条款。
