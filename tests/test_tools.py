#!/usr/bin/env python3
"""
工具测试文件 - 测试 search、google_scholar、visit 三个工具的功能
"""

import os
import sys
import json
import time
import unittest
from typing import Dict, List, Any
from unittest.mock import Mock, patch

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference.tool_search import Search
from inference.tool_scholar import Scholar
from inference.tool_visit import Visit


class ToolTestBase(unittest.TestCase):
    """测试基类，提供通用功能"""

    def setUp(self):
        """测试前的准备工作"""
        print(f"\n{'='*50}")
        print(f"开始测试: {self._testMethodName}")
        print(f"{'='*50}")

    def tearDown(self):
        """测试后的清理工作"""
        print(f"完成测试: {self._testMethodName}")
        print(f"{'='*50}")

    def check_environment_variable(self, var_name: str) -> bool:
        """检查环境变量是否存在且不为空"""
        value = os.environ.get(var_name, "")
        exists = bool(value and value.strip())
        print(f"环境变量 {var_name}: {'✓' if exists else '✗'}")
        if not exists:
            print(f"  警告: {var_name} 未设置或为空，相关测试可能会失败")
        return exists

    def print_test_result(self, test_name: str, success: bool, details: str = ""):
        """打印测试结果"""
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
        if details:
            print(f"  详情: {details}")


class TestSearchTool(ToolTestBase):
    """测试 search 工具"""

    def setUp(self):
        super().setUp()
        self.search_tool = Search()
        self.has_serper_key = self.check_environment_variable("SERPER_KEY_ID")

    def test_single_query_search(self):
        """测试单个查询搜索"""
        if not self.has_serper_key:
            self.skipTest("SERPER_KEY_ID 未设置")

        test_query = ["Python programming language"]
        print(f"测试查询: {test_query}")

        try:
            result = self.search_tool.call({"query": test_query})
            success = bool(result and len(result) > 10)
            details = f"返回结果长度: {len(result) if result else 0}"
            self.print_test_result("单个查询搜索", success, details)
            self.assertTrue(success, "搜索应该返回有效结果")
        except Exception as e:
            self.print_test_result("单个查询搜索", False, f"异常: {str(e)}")
            self.fail(f"搜索测试失败: {str(e)}")

    def test_multiple_query_search(self):
        """测试多个查询搜索"""
        if not self.has_serper_key:
            self.skipTest("SERPER_KEY_ID 未设置")

        test_queries = ["Python programming", "Machine learning basics"]
        print(f"测试查询: {test_queries}")

        try:
            result = self.search_tool.call({"query": test_queries})
            success = bool(result and len(result) > 20)
            details = f"返回结果长度: {len(result) if result else 0}"
            self.print_test_result("多个查询搜索", success, details)
            self.assertTrue(success, "多查询搜索应该返回有效结果")
        except Exception as e:
            self.print_test_result("多个查询搜索", False, f"异常: {str(e)}")
            self.fail(f"多查询搜索测试失败: {str(e)}")

    def test_chinese_query_search(self):
        """测试中文查询搜索"""
        if not self.has_serper_key:
            self.skipTest("SERPER_KEY_ID 未设置")

        test_query = ["人工智能 机器学习"]
        print(f"测试查询: {test_query}")

        try:
            result = self.search_tool.call({"query": test_query})
            success = bool(result and len(result) > 10)
            details = f"返回结果长度: {len(result) if result else 0}"
            self.print_test_result("中文查询搜索", success, details)
            self.assertTrue(success, "中文搜索应该返回有效结果")
        except Exception as e:
            self.print_test_result("中文查询搜索", False, f"异常: {str(e)}")
            self.fail(f"中文搜索测试失败: {str(e)}")

    def test_invalid_query_format(self):
        """测试无效查询格式"""
        invalid_queries = [
            {},  # 缺少 query 字段
            {"query": []},  # 空查询列表
            {"query": [""]},  # 空查询字符串
            {"not_query": ["test"]},  # 错误字段名
        ]

        for i, query in enumerate(invalid_queries):
            print(f"测试无效查询格式 {i+1}: {query}")
            try:
                result = self.search_tool.call(query)
                # 工具应该返回错误信息，而不是抛出异常
                success = isinstance(result, str) and ("Invalid" in result or "Error" in result)
                details = f"返回: {result[:100] if result else 'None'}..."
                self.print_test_result(f"无效查询格式 {i+1}", success, details)
            except Exception as e:
                self.print_test_result(f"无效查询格式 {i+1}", False, f"异常: {str(e)}")


class TestScholarTool(ToolTestBase):
    """测试 google_scholar 工具"""

    def setUp(self):
        super().setUp()
        self.scholar_tool = Scholar()
        self.has_serper_key = self.check_environment_variable("SERPER_KEY_ID")

    def test_single_scholar_search(self):
        """测试单个学术搜索"""
        if not self.has_serper_key:
            self.skipTest("SERPER_KEY_ID 未设置")

        test_query = ["attention mechanism neural networks"]
        print(f"测试学术查询: {test_query}")

        try:
            result = self.scholar_tool.call({"query": test_query})
            success = bool(result and len(result) > 10)
            details = f"返回结果长度: {len(result) if result else 0}"
            self.print_test_result("单个学术搜索", success, details)
            self.assertTrue(success, "学术搜索应该返回有效结果")
        except Exception as e:
            self.print_test_result("单个学术搜索", False, f"异常: {str(e)}")
            self.fail(f"学术搜索测试失败: {str(e)}")

    def test_multiple_scholar_search(self):
        """测试多个学术搜索"""
        if not self.has_serper_key:
            self.skipTest("SERPER_KEY_ID 未设置")

        test_queries = ["transformer architecture", "bert language model"]
        print(f"测试学术查询: {test_queries}")

        try:
            result = self.scholar_tool.call({"query": test_queries})
            success = bool(result and len(result) > 20)
            details = f"返回结果长度: {len(result) if result else 0}"
            self.print_test_result("多个学术搜索", success, details)
            self.assertTrue(success, "多学术查询搜索应该返回有效结果")
        except Exception as e:
            self.print_test_result("多个学术搜索", False, f"异常: {str(e)}")
            self.fail(f"多学术搜索测试失败: {str(e)}")


class TestVisitTool(ToolTestBase):
    """测试 visit 工具"""

    def setUp(self):
        super().setUp()
        self.visit_tool = Visit()
        self.has_jina_key = self.check_environment_variable("JINA_API_KEYS")

    def test_single_url_visit(self):
        """测试单个URL访问"""
        if not self.has_jina_key:
            self.skipTest("JINA_API_KEYS 未设置")

        test_url = "https://httpbin.org/json"
        test_goal = "测试基本的网页访问功能"
        print(f"测试URL: {test_url}")
        print(f"访问目标: {test_goal}")

        try:
            result = self.visit_tool.call({"url": test_url, "goal": test_goal})
            success = bool(result and len(result) > 20)
            details = f"返回结果长度: {len(result) if result else 0}"
            self.print_test_result("单个URL访问", success, details)
            self.assertTrue(success, "URL访问应该返回有效结果")
        except Exception as e:
            self.print_test_result("单个URL访问", False, f"异常: {str(e)}")
            self.fail(f"URL访问测试失败: {str(e)}")

    def test_multiple_url_visit(self):
        """测试多个URL访问"""
        if not self.has_jina_key:
            self.skipTest("JINA_API_KEYS 未设置")

        test_urls = [
            "https://httpbin.org/json",
            "https://httpbin.org/headers"
        ]
        test_goal = "测试多个网页的访问功能"
        print(f"测试URL列表: {test_urls}")
        print(f"访问目标: {test_goal}")

        try:
            result = self.visit_tool.call({"url": test_urls, "goal": test_goal})
            success = bool(result and len(result) > 40)
            details = f"返回结果长度: {len(result) if result else 0}"
            self.print_test_result("多个URL访问", success, details)
            self.assertTrue(success, "多URL访问应该返回有效结果")
        except Exception as e:
            self.print_test_result("多个URL访问", False, f"异常: {str(e)}")
            self.fail(f"多URL访问测试失败: {str(e)}")

    def test_invalid_url_format(self):
        """测试无效URL格式"""
        invalid_cases = [
            {},  # 缺少必要字段
            {"url": "not-a-url", "goal": "test"},  # 无效URL
            {"url": "https://example.com"},  # 缺少goal
            {"goal": "test"},  # 缺少url
        ]

        for i, case in enumerate(invalid_cases):
            print(f"测试无效URL格式 {i+1}: {case}")
            try:
                result = self.visit_tool.call(case)
                # 应该返回错误信息
                success = isinstance(result, str) and ("Invalid" in result or "Error" in result or "Failed" in result)
                details = f"返回: {result[:100] if result else 'None'}..."
                self.print_test_result(f"无效URL格式 {i+1}", success, details)
            except Exception as e:
                self.print_test_result(f"无效URL格式 {i+1}", False, f"异常: {str(e)}")


class ToolIntegrationTest(ToolTestBase):
    """工具集成测试"""

    def setUp(self):
        super().setUp()
        self.has_serper_key = self.check_environment_variable("SERPER_KEY_ID")
        self.has_jina_key = self.check_environment_variable("JINA_API_KEYS")

    def test_search_then_visit_workflow(self):
        """测试搜索后访问的工作流"""
        if not self.has_serper_key or not self.has_jina_key:
            self.skipTest("缺少必需的API密钥")

        # 第一步：搜索相关网页
        search_query = ["Python official documentation"]
        print(f"步骤1: 搜索 {search_query}")

        try:
            search_result = Search().call({"query": search_query})
            if not search_result:
                self.print_test_result("搜索后访问工作流", False, "搜索未返回结果")
                return

            print(f"搜索成功，结果长度: {len(search_result)}")

            # 第二步：访问第一个找到的URL（简化测试，使用固定URL）
            test_url = "https://www.python.org"
            visit_goal = "获取Python官方网站的基本信息"
            print(f"步骤2: 访问 {test_url}")

            visit_result = Visit().call({"url": test_url, "goal": visit_goal})

            success = bool(visit_result and len(visit_result) > 20)
            details = f"搜索结果: {len(search_result)} 字符, 访问结果: {len(visit_result) if visit_result else 0} 字符"
            self.print_test_result("搜索后访问工作流", success, details)
            self.assertTrue(success, "搜索后访问工作流应该成功")

        except Exception as e:
            self.print_test_result("搜索后访问工作流", False, f"异常: {str(e)}")
            self.fail(f"集成测试失败: {str(e)}")


def run_environment_check():
    """运行环境检查"""
    print(f"\n{'='*60}")
    print("环境变量检查")
    print(f"{'='*60}")

    env_vars = [
        "SERPER_KEY_ID",
        "JINA_API_KEYS",
        "OPENROUTER_API_KEY",
        "API_KEY",
        "API_BASE"
    ]

    for var in env_vars:
        value = os.environ.get(var, "")
        status = "✓" if value and value.strip() else "✗"
        masked_value = value[:8] + "..." if len(value) > 8 else value
        print(f"{var:20} {status} {masked_value if status == '✓' else '(未设置)'}")


def main():
    """主测试函数"""
    print("DeepResearch 工具测试套件")
    print("=" * 60)

    # 环境检查
    run_environment_check()

    # 创建测试套件
    test_suite = unittest.TestSuite()

    # 添加测试用例
    test_classes = [
        TestSearchTool,
        TestScholarTool,
        TestVisitTool,
        ToolIntegrationTest
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2, stream=open('test_results.txt', 'w', encoding='utf-8'))
    result = runner.run(test_suite)

    # 输出摘要
    print(f"\n{'='*60}")
    print("测试摘要")
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