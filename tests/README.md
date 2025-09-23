# DeepResearch 工具测试套件

本测试套件用于验证 DeepResearch 系统中的三个核心工具：
- `search` - 网络搜索工具
- `google_scholar` - 学术搜索工具
- `visit` - 网页访问工具

## 文件结构

```
tests/
├── README.md                    # 本说明文档
├── test_tools.py               # 主要功能测试
├── test_tool_config.py         # 配置和初始化测试
├── run_tests.py               # 测试运行脚本
└── test_results.txt           # 测试结果输出文件
```

## 环境要求

运行测试前需要设置以下环境变量：

### 必需的环境变量

| 环境变量名 | 用途 | 工具依赖 |
|-----------|------|----------|
| `SERPER_KEY_ID` | Google Serp API 密钥 | search, google_scholar |
| `JINA_API_KEYS` | Jina Reader API 密钥 | visit |

### 可选的环境变量

| 环境变量名 | 用途 | 默认值 |
|-----------|------|--------|
| `VISIT_SERVER_TIMEOUT` | 访问工具超时时间（秒） | 200 |
| `WEBCONTENT_MAXLENGTH` | 网页内容最大长度 | 150000 |
| `API_KEY` | LLM API 密钥 | - |
| `API_BASE` | LLM API 基础URL | - |
| `SUMMARY_MODEL_NAME` | 摘要模型名称 | - |

## 快速开始

### 1. 环境检查

```bash
# 进入项目根目录
cd /home/chencheng/py/src/DeepResearch

# 运行环境检查
python -c "
import os
env_vars = ['SERPER_KEY_ID', 'JINA_API_KEYS']
for var in env_vars:
    value = os.environ.get(var, '')
    status = '✓' if value and value.strip() else '✗'
    print(f'{var}: {status}')
"
```

### 2. 运行配置测试

```bash
# 测试工具配置和初始化
python tests/test_tool_config.py
```

### 3. 运行功能测试

```bash
# 运行所有功能测试
python tests/test_tools.py
```

### 4. 使用测试脚本

```bash
# 运行所有测试
python tests/run_tests.py

# 只运行配置测试
python tests/run_tests.py --config

# 只运行功能测试
python tests/run_tests.py --functional

# 详细输出模式
python tests/run_tests.py --verbose
```

## 测试内容

### test_tool_config.py

**配置测试项目：**
- ✅ 工具初始化
- ✅ 参数定义验证
- ✅ 环境变量依赖检查
- ✅ 默认值设置
- ✅ 错误处理机制
- ✅ 工具描述验证
- ✅ 工具注册状态

### test_tools.py

**功能测试项目：**

#### Search 工具测试
- 单个查询搜索
- 多个查询搜索
- 中文查询搜索
- 无效查询格式处理

#### Scholar 工具测试
- 单个学术搜索
- 多个学术搜索
- 学术结果质量验证

#### Visit 工具测试
- 单个URL访问
- 多个URL访问
- 内容提取质量
- 无效URL处理

#### 集成测试
- 搜索后访问工作流
- 工具链协同工作
- 错误恢复机制

## 测试结果解读

### 成功输出示例

```
==================================================
环境变量检查
==================================================
SERPER_KEY_ID        ✓ sk-123456...
JINA_API_KEYS        ✓ jina_123456...
OPENROUTER_API_KEY   ✓ sk-or-123456...

==================================================
开始测试: test_single_query_search
==================================================
测试查询: ['Python programming language']
单个查询搜索: ✓ 通过
  详情: 返回结果长度: 2048
```

### 常见错误及解决方案

#### 1. 环境变量未设置

**错误：** `SKIP: SERPER_KEY_ID 未设置`

**解决方案：**
```bash
export SERPER_KEY_ID="your_serper_api_key"
export JINA_API_KEYS="your_jina_api_key"
```

#### 2. API 密钥无效

**错误：** `Invalid JINA_API_KEYS. Please check your API key.`

**解决方案：**
- 检查 API 密钥是否正确
- 确认 API 密钥是否有效且未过期
- 检查账户余额是否充足

#### 3. 网络连接问题

**错误：** `Failed to read page due to connection error.`

**解决方案：**
- 检查网络连接
- 确认防火墙设置
- 尝试使用代理

#### 4. 速率限制

**错误：** HTTP 429 错误

**解决方案：**
- 降低请求频率
- 检查 API 使用限制
- 等待一段时间后重试

## API 密钥获取

### Serper API (搜索工具)
1. 访问 [https://serper.dev/](https://serper.dev/)
2. 注册账户
3. 获取 API 密钥
4. 设置环境变量：`export SERPER_KEY_ID="your_key"`

### Jina API (访问工具)
1. 访问 [https://jina.ai/reader/](https://jina.ai/reader/)
2. 注册账户
3. 获取 API 密钥
4. 设置环境变量：`export JINA_API_KEYS="your_key"`

## 自定义测试

### 添加新的测试用例

```python
class CustomToolTest(ToolTestBase):
    def test_custom_functionality(self):
        # 你的测试逻辑
        pass
```

### 跳过特定测试

```python
def test_expensive_operation(self):
    if not os.environ.get('RUN_EXPENSIVE_TESTS'):
        self.skipTest("跳过耗时测试")
    # 测试逻辑
```

### 条件测试

```python
def test_network_dependent(self):
    try:
        # 网络相关测试
        pass
    except requests.ConnectionError:
        self.skipTest("网络不可用")
```

## 故障排除

### 1. 导入错误

如果遇到导入错误，确保：
- 在项目根目录运行测试
- Python 路径设置正确
- 所有依赖已安装

### 2. 测试超时

如果测试运行超时：
- 检查网络连接
- 减少测试查询数量
- 调整超时设置

### 3. 内存不足

如果遇到内存问题：
- 减少并发测试数量
- 降低内容长度限制
- 清理测试结果文件

## 贡献指南

1. 新增测试用例时请遵循现有命名规范
2. 确保测试独立，不依赖执行顺序
3. 添加适当的错误处理和清理逻辑
4. 更新文档说明

## 许可证

本测试套件遵循项目主许可证。