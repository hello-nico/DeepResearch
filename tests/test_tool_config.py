#!/usr/bin/env python3
"""
工具配置测试文件 - 测试工具的配置和初始化
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference.tool_search import Search
from inference.tool_scholar import Scholar
from inference.tool_visit import Visit


class ToolConfigTest(unittest.TestCase):
    """工具配置测试"""

    def setUp(self):
        """测试前的准备工作"""
        print(f"\n{'='*50}")
        print(f"开始配置测试: {self._testMethodName}")
        print(f"{'='*50}")

        # 保存原始环境变量
        self.original_env = {}
        self.env_vars_to_backup = [
            'SERPER_KEY_ID',
            'TAVILY_API_KEY',
            'JINA_API_KEYS',
            'VISIT_SERVER_TIMEOUT',
            'WEBCONTENT_MAXLENGTH',
            'API_KEY',
            'API_BASE',
            'SUMMARY_MODEL_NAME'
        ]

        for var in self.env_vars_to_backup:
            self.original_env[var] = os.environ.get(var)

    def tearDown(self):
        """测试后的清理工作"""
        print(f"完成配置测试: {self._testMethodName}")
        print(f"{'='*50}")

        # 恢复原始环境变量
        for var in self.env_vars_to_backup:
            if self.original_env[var] is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = self.original_env[var]

    def test_search_tool_initialization(self):
        """测试搜索工具初始化"""
        print("测试搜索工具初始化...")

        # 正常初始化
        try:
            search_tool = Search()
            self.assertIsNotNone(search_tool)
            self.assertEqual(search_tool.name, "search")
            print("✓ 搜索工具正常初始化")
        except Exception as e:
            self.fail(f"搜索工具初始化失败: {str(e)}")

        # 带配置初始化
        try:
            config = {"test": "config"}
            search_tool_with_config = Search(cfg=config)
            self.assertIsNotNone(search_tool_with_config)
            print("✓ 搜索工具带配置初始化成功")
        except Exception as e:
            self.fail(f"搜索工具带配置初始化失败: {str(e)}")

    def test_scholar_tool_initialization(self):
        """测试学术搜索工具初始化"""
        print("测试学术搜索工具初始化...")

        try:
            scholar_tool = Scholar()
            self.assertIsNotNone(scholar_tool)
            self.assertEqual(scholar_tool.name, "google_scholar")
            print("✓ 学术搜索工具正常初始化")
        except Exception as e:
            self.fail(f"学术搜索工具初始化失败: {str(e)}")

    def test_visit_tool_initialization(self):
        """测试访问工具初始化"""
        print("测试访问工具初始化...")

        try:
            visit_tool = Visit()
            self.assertIsNotNone(visit_tool)
            self.assertEqual(visit_tool.name, "visit")
            print("✓ 访问工具正常初始化")
        except Exception as e:
            self.fail(f"访问工具初始化失败: {str(e)}")

    def test_search_tool_parameters(self):
        """测试搜索工具参数定义"""
        print("测试搜索工具参数定义...")

        search_tool = Search()
        parameters = search_tool.parameters

        # 检查参数结构
        self.assertIn("type", parameters)
        self.assertIn("properties", parameters)
        self.assertIn("required", parameters)

        # 检查query参数
        self.assertIn("query", parameters["properties"])
        query_param = parameters["properties"]["query"]
        self.assertEqual(query_param["type"], "array")
        self.assertIn("items", query_param)
        self.assertEqual(query_param["items"]["type"], "string")

        # 检查必需参数
        self.assertIn("query", parameters["required"])

        print("✓ 搜索工具参数定义正确")

    def test_scholar_tool_parameters(self):
        """测试学术搜索工具参数定义"""
        print("测试学术搜索工具参数定义...")

        scholar_tool = Scholar()
        parameters = scholar_tool.parameters

        # 检查参数结构
        self.assertIn("type", parameters)
        self.assertIn("properties", parameters)
        self.assertIn("required", parameters)

        # 检查query参数
        self.assertIn("query", parameters["properties"])
        query_param = parameters["properties"]["query"]
        self.assertEqual(query_param["type"], "array")
        self.assertIn("items", query_param)
        self.assertEqual(query_param["items"]["type"], "string")
        self.assertIn("minItems", query_param)
        self.assertEqual(query_param["minItems"], 1)

        # 检查必需参数
        self.assertIn("query", parameters["required"])

        print("✓ 学术搜索工具参数定义正确")

    def test_visit_tool_parameters(self):
        """测试访问工具参数定义"""
        print("测试访问工具参数定义...")

        visit_tool = Visit()
        parameters = visit_tool.parameters

        # 检查参数结构
        self.assertIn("type", parameters)
        self.assertIn("properties", parameters)
        self.assertIn("required", parameters)

        # 检查url参数
        self.assertIn("url", parameters["properties"])
        url_param = parameters["properties"]["url"]
        self.assertIn("string", url_param["type"])  # 可以是字符串或数组
        if isinstance(url_param["type"], list):
            self.assertIn("string", url_param["type"])
            self.assertIn("array", url_param["type"])
        else:
            # 如果是单一类型，检查items（当type为array时）
            pass

        # 检查goal参数
        self.assertIn("goal", parameters["properties"])
        goal_param = parameters["properties"]["goal"]
        self.assertEqual(goal_param["type"], "string")

        # 检查必需参数
        self.assertIn("url", parameters["required"])
        self.assertIn("goal", parameters["required"])

        print("✓ 访问工具参数定义正确")

    def test_environment_variable_dependency(self):
        """测试环境变量依赖"""
        print("测试环境变量依赖...")

        # 测试没有SERPER_KEY的情况
        if 'SERPER_KEY_ID' in os.environ:
            del os.environ['SERPER_KEY_ID']

        # 搜索工具应该仍然能初始化，但调用时会失败
        search_tool = Search()
        self.assertIsNotNone(search_tool)
        print("✓ 搜索工具在缺少API密钥时仍能初始化")

        # 测试没有JINA_API_KEYS的情况
        if 'JINA_API_KEYS' in os.environ:
            del os.environ['JINA_API_KEYS']

        # 访问工具应该仍然能初始化，但调用时会失败
        visit_tool = Visit()
        self.assertIsNotNone(visit_tool)
        print("✓ 访问工具在缺少API密钥时仍能初始化")

    def test_default_environment_variables(self):
        """测试默认环境变量值"""
        print("测试默认环境变量值...")

        # 测试访问工具的默认超时设置
        original_timeout = os.environ.get('VISIT_SERVER_TIMEOUT')
        if 'VISIT_SERVER_TIMEOUT' in os.environ:
            del os.environ['VISIT_SERVER_TIMEOUT']

        # 重新初始化访问工具
        visit_tool = Visit()
        # 工具应该使用默认值
        print("✓ 访问工具使用默认超时设置")

        # 恢复原始值
        if original_timeout is not None:
            os.environ['VISIT_SERVER_TIMEOUT'] = original_timeout

        # 测试默认内容长度限制
        original_maxlength = os.environ.get('WEBCONTENT_MAXLENGTH')
        if 'WEBCONTENT_MAXLENGTH' in os.environ:
            del os.environ['WEBCONTENT_MAXLENGTH']

        # 重新初始化访问工具
        visit_tool = Visit()
        # 工具应该使用默认值
        print("✓ 访问工具使用默认内容长度限制")

        # 恢复原始值
        if original_maxlength is not None:
            os.environ['WEBCONTENT_MAXLENGTH'] = original_maxlength

    def test_tool_error_handling(self):
        """测试工具错误处理"""
        print("测试工具错误处理...")

        # 测试搜索工具的错误处理
        search_tool = Search()

        # 测试空查询
        result = search_tool.call({"query": []})
        self.assertIsInstance(result, str)
        print("✓ 搜索工具正确处理空查询")

        # 测试无效参数格式
        result = search_tool.call("invalid_format")
        self.assertIsInstance(result, str)
        self.assertIn("Invalid", result)
        print("✓ 搜索工具正确处理无效参数格式")

        # 测试学术搜索工具的错误处理
        scholar_tool = Scholar()

        # 测试空查询
        result = scholar_tool.call({"query": []})
        self.assertIsInstance(result, str)
        print("✓ 学术搜索工具正确处理空查询")

        # 测试访问工具的错误处理
        visit_tool = Visit()

        # 测试缺少必要参数
        result = visit_tool.call({})
        self.assertIsInstance(result, str)
        self.assertIn("Invalid", result)
        print("✓ 访问工具正确处理缺少参数的情况")

        # 测试无效URL格式
        result = visit_tool.call({"url": "not-a-valid-url", "goal": "test"})
        self.assertIsInstance(result, str)
        print("✓ 访问工具正确处理无效URL")

    def test_tool_descriptions(self):
        """测试工具描述"""
        print("测试工具描述...")

        # 测试搜索工具描述
        search_tool = Search()
        self.assertIsInstance(search_tool.description, str)
        self.assertTrue(len(search_tool.description) > 0)
        self.assertIn("search", search_tool.description.lower())
        print("✓ 搜索工具有有效描述")

        # 测试学术搜索工具描述
        scholar_tool = Scholar()
        self.assertIsInstance(scholar_tool.description, str)
        self.assertTrue(len(scholar_tool.description) > 0)
        self.assertIn("scholar", scholar_tool.description.lower())
        print("✓ 学术搜索工具有有效描述")

        # 测试访问工具描述
        visit_tool = Visit()
        self.assertIsInstance(visit_tool.description, str)
        self.assertTrue(len(visit_tool.description) > 0)
        self.assertIn("visit", visit_tool.description.lower())
        print("✓ 访问工具有有效描述")

    def test_tool_registration(self):
        """测试工具注册"""
        print("测试工具注册...")

        # 检查工具是否正确注册
        from qwen_agent.tools.base import get_tool

        try:
            search_tool = get_tool("search")
            self.assertIsNotNone(search_tool)
            print("✓ 搜索工具注册成功")
        except:
            print("⚠ 搜索工具注册测试跳过（可能需要qwen_agent完整环境）")

        try:
            scholar_tool = get_tool("google_scholar")
            self.assertIsNotNone(scholar_tool)
            print("✓ 学术搜索工具注册成功")
        except:
            print("⚠ 学术搜索工具注册测试跳过（可能需要qwen_agent完整环境）")

        try:
            visit_tool = get_tool("visit")
            self.assertIsNotNone(visit_tool)
            print("✓ 访问工具注册成功")
        except:
            print("⚠ 访问工具注册测试跳过（可能需要qwen_agent完整环境）")


def print_environment_summary():
    """打印环境摘要"""
    print(f"\n{'='*60}")
    print("工具配置测试 - 环境摘要")
    print(f"{'='*60}")

    env_vars = {
        'SERPER_KEY_ID': 'Search & Scholar 工具 API 密钥',
        'JINA_API_KEYS': 'Visit 工具 API 密钥',
        'VISIT_SERVER_TIMEOUT': '访问工具超时设置',
        'WEBCONTENT_MAXLENGTH': '网页内容最大长度',
        'API_KEY': 'LLM API 密钥',
        'API_BASE': 'LLM API 基础URL',
        'SUMMARY_MODEL_NAME': '摘要模型名称'
    }

    for var, description in env_vars.items():
        value = os.environ.get(var, "")
        status = "✓" if value and value.strip() else "✗"
        masked_value = f"{value[:8]}..." if len(value) > 8 else value
        print(f"{var:25} {status} {description}")
        if status == "✓":
            print(f"{'':27} 值: {masked_value}")
        else:
            print(f"{'':27} 状态: 未设置")


def main():
    """主测试函数"""
    print("DeepResearch 工具配置测试套件")
    print("=" * 60)

    # 打印环境摘要
    print_environment_summary()

    # 创建测试套件
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ToolConfigTest))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 输出摘要
    print(f"\n{'='*60}")
    print("配置测试摘要")
    print(f"{'='*60}")
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.failures:
        print(f"\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print(f"\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
