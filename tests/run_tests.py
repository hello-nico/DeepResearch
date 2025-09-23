"""
DeepResearch 工具测试运行脚本
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path


def check_environment():
    """检查测试环境"""
    print("=" * 60)
    print("环境检查")
    print("=" * 60)

    required_vars = ['SERPER_KEY_ID', 'JINA_API_KEYS']
    optional_vars = ['OPENROUTER_API_KEY']

    missing_required = []

    for var in required_vars:
        value = os.environ.get(var, '')
        if value and value.strip():
            print(f"✓ {var}: 已设置")
        else:
            print(f"✗ {var}: 未设置")
            missing_required.append(var)

    for var in optional_vars:
        value = os.environ.get(var, '')
        if value and value.strip():
            print(f"✓ {var}: 已设置")
        else:
            print(f"- {var}: 未设置（可选）")

    if missing_required:
        print(f"\n⚠️  缺少必需的环境变量: {', '.join(missing_required)}")
        print("   某些测试可能会被跳过或失败")
        return False

    print("\n✅ 环境检查通过")
    return True


def run_config_test(verbose=False):
    """运行配置测试"""
    print("\n" + "=" * 60)
    print("运行配置测试")
    print("=" * 60)

    cmd = [sys.executable, "test_tool_config.py"]
    if verbose:
        cmd.append("-v")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="tests")
        print("配置测试输出:")
        print("-" * 40)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"配置测试运行失败: {str(e)}")
        return False


def run_functional_test(verbose=False):
    """运行功能测试"""
    print("\n" + "=" * 60)
    print("运行功能测试")
    print("=" * 60)

    cmd = [sys.executable, "test_tools.py"]
    if verbose:
        cmd.append("-v")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="tests")
        print("功能测试输出:")
        print("-" * 40)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"功能测试运行失败: {str(e)}")
        return False


def run_quick_test():
    """运行快速测试（仅配置测试）"""
    print("\n" + "=" * 60)
    print("运行快速测试")
    print("=" * 60)

    success = run_config_test(verbose=True)

    if success:
        print("\n✅ 快速测试通过")
    else:
        print("\n❌ 快速测试失败")

    return success


def generate_test_report():
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("生成测试报告")
    print("=" * 60)

    report_file = "tests/test_report.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# DeepResearch 工具测试报告\n\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # 环境信息
        f.write("## 环境信息\n\n")
        env_vars = ['SERPER_KEY_ID', 'JINA_API_KEYS', 'OPENROUTER_API_KEY']
        for var in env_vars:
            value = os.environ.get(var, '')
            status = "✅ 已设置" if value and value.strip() else "❌ 未设置"
            f.write(f"- **{var}**: {status}\n")
        f.write("\n")

        # 检查测试结果文件
        result_files = ["tests/test_results.txt"]

        for result_file in result_files:
            if Path(result_file).exists():
                f.write(f"## {Path(result_file).name} 结果\n\n")
                f.write("```\n")
                with open(result_file, 'r', encoding='utf-8') as rf:
                    f.write(rf.read())
                f.write("\n```\n\n")

    print(f"📄 测试报告已生成: {report_file}")
    return report_file


def main():
    parser = argparse.ArgumentParser(description='DeepResearch 工具测试运行器')
    parser.add_argument('--config', action='store_true', help='仅运行配置测试')
    parser.add_argument('--functional', action='store_true', help='仅运行功能测试')
    parser.add_argument('--quick', action='store_true', help='运行快速测试（仅配置测试）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--no-env-check', action='store_true', help='跳过环境检查')
    parser.add_argument('--report', action='store_true', help='生成测试报告')

    args = parser.parse_args()

    print("🧪 DeepResearch 工具测试套件")
    print("=" * 60)

    # 检查是否在正确的目录
    if not Path("tests").exists():
        print("❌ 错误: 请在项目根目录运行此脚本")
        sys.exit(1)

    # 切换到tests目录
    os.chdir("tests")

    # 环境检查
    if not args.no_env_check:
        env_ok = check_environment()
        if not env_ok and not args.quick:
            print("\n⚠️  环境检查失败，但继续运行测试...")

    start_time = time.time()
    config_success = True
    functional_success = True

    try:
        if args.quick:
            # 快速测试模式
            config_success = run_quick_test()

        elif args.config:
            # 仅配置测试
            config_success = run_config_test(args.verbose)

        elif args.functional:
            # 仅功能测试
            functional_success = run_functional_test(args.verbose)

        else:
            # 运行所有测试
            if args.verbose:
                print("\n🔄 运行完整测试套件...")

            config_success = run_config_test(args.verbose)
            functional_success = run_functional_test(args.verbose)

        # 计算总耗时
        elapsed_time = time.time() - start_time

        # 输出结果摘要
        print("\n" + "=" * 60)
        print("测试结果摘要")
        print("=" * 60)
        print(f"⏱️  总耗时: {elapsed_time:.2f} 秒")

        if args.quick:
            print(f"📋 快速测试: {'✅ 通过' if config_success else '❌ 失败'}")
        else:
            if args.config:
                print(f"⚙️  配置测试: {'✅ 通过' if config_success else '❌ 失败'}")
            elif args.functional:
                print(f"🔧 功能测试: {'✅ 通过' if functional_success else '❌ 失败'}")
            else:
                print(f"⚙️  配置测试: {'✅ 通过' if config_success else '❌ 失败'}")
                print(f"🔧 功能测试: {'✅ 通过' if functional_success else '❌ 失败'}")

        # 总体结果
        overall_success = config_success and functional_success
        print(f"\n🎯 总体结果: {'✅ 所有测试通过' if overall_success else '❌ 部分测试失败'}")

        # 生成报告
        if args.report:
            report_file = generate_test_report()
            print(f"📄 报告文件: {report_file}")

        # 返回适当的退出码
        sys.exit(0 if overall_success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试运行出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()