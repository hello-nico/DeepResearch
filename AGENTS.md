# Repository Guidelines

## 项目结构与模块组织

- `inference/` 承载核心 ReAct 推理链、工具接口与 `file_tools/` 等子模块，是日常功能开发的首选入口；修改时同步更新该目录下的 `claude.md`，保持工具说明与参数示例一致。
- `Agent/` 管理训练与数据合成脚本，生成的示例数据通常会回流到 `inference/eval_data/`；若新增实验，请在目录内新增子文件夹存放配置与文档，避免与已有流水线混用。
- `WebAgent/` 聚焦浏览器自动化家族，包含多套代理原型与依赖，遵循子目录自述文档约定；跨目录共用组件建议抽取到顶层 `Agent/` 或 `inference/` 以减少重复。
- `evaluation/` 收录官方基准脚本与提示词，`examples/` 提供最小可复现样例，`assets/` 仅存放公开图像与可视化资源；所有临时产物请输出至 `log/` 或 `.gitignore` 遮罩路径。

## 构建、测试与开发命令

- 环境与依赖统一通过 `uv sync` 安装，保持与 `.python-version` 指定的 3.11 一致；必要时使用 `uv pip install <pkg>` 临时拉取调试依赖，并在提交前回卷变更。
- 快速查看 CLI 入口：`uv run python main.py --help`；单实例推理采用 `bash inference/run_react_infer.sh`，根据脚本注释配置 `MODEL_PATH`、`DATASET`、API key 等变量。
- 多代理或批量测试可运行 `uv run python inference/run_multi_react.py --help` 获取参数说明，再结合 `tool_*.py` 中定义的工具开关进行实验。
- 评估流程使用 `uv run python evaluation/evaluate_*.py --dataset <path> --output ./log/<run>`；提交 PR 前附上关键指标与结果摘要，便于复核。

## 编码风格与命名规范

- 遵循 PEP 8、类型提示与四空格缩进；模块、函数、变量使用 `snake_case`，类与 dataclass 采用 `PascalCase`，常量保持 `UPPER_SNAKE_CASE`，新文件命名需匹配其职责。
- 统一导入顺序：标准库→第三方→本地模块，使用空行分组；新增公共 API 需在 docstring 给出参数和返回示例。
- 提交前运行 `uv run ruff check .` 与 `uv run black --check .`，若格式化带来大量改动，请在独立 commit 中处理以简化审阅。

## 测试指引

- 单元测试放置于 `tests/` 并镜像源目录结构，命名格式 `test_<module>.py`；对交互式代理逻辑使用假造工具响应或 fixture，确保行为可重复。
- 通过 `uv run pytest --maxfail=1 --disable-warnings` 获取快速反馈；关键路径需覆盖正常、异常与边界情形，推荐使用 `pytest.mark.parametrize` 扩展样例。
- 评估脚本视为集成测试，更新提示词或数据集后务必重新运行相关 `evaluate_*.py`，在 PR 描述中列出输入规模、运行命令与最关心指标。

## 提交与合并规范

- Commit 信息采用 Conventional Commits，例如 `feat: add scholar search tool`、`fix: guard empty tool response` 或 `chore: sync uv lock`；每次提交聚焦单一主题，便于回溯。
- 打开 PR 时附带变更动机、主要实现点、验证命令、依赖与截图/日志，必要时链接 issue；禁止将尚未生效的密钥或私有数据写入仓库。
- 在获得审阅通过前禁止强推，若需 rebase 请提前沟通；确认 `git status` 干净后再进行多端合并。

## 安全与配置提示

- 所有密钥、cookie、私有模型路径与服务凭据仅放入 `.env` 或本地凭据管理器，切勿提交；示例值可写入 `.env.example`。
- 网络访问脚本默认遵循最小权限原则，新增外部依赖需在 PR 中解释用途并更新 `requirements.txt` 与 `uv.lock`。
- 调整依赖时先在本地运行 `uv run pytest`、`uv run ruff check .`、`uv run black --check .` 三项校验，确保锁文件变更有充分理由并记录在 PR 描述。
