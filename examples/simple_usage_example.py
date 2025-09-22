"""
DeepResearch 简单使用示例
展示基本的DeepResearch调用方式
"""

import json
import os
import sys

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference.react_agent import MultiTurnReactAgent


def simple_research_example():
    """简单的研究示例"""
    print("DeepResearch 简单使用示例")
    print("="*50)

    # 配置模型
    model_path = "alibaba/tongyi-deepresearch-30b-a3b"  # OpenRouter 模型名称
    planning_port = 6001

    # 配置LLM - OpenRouter API 配置
    llm_cfg = {
        'model': model_path,
        'generate_cfg': {
            'max_input_tokens': 320000,
            'max_retries': 10,
            'temperature': 0.6,
            'top_p': 0.95,
            'presence_penalty': 1.1
        },
        'model_type': 'openai'  # 使用 OpenAI 兼容的 API
    }

    # 创建Agent
    agent = MultiTurnReactAgent(
        llm=llm_cfg,
        function_list=["search", "visit", "google_scholar", "PythonInterpreter"]
    )

    # 示例问题
    questions = [
        "What is GraphRAG technology?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question}")
        print("-" * 50)

        # 构造输入数据
        input_data = {
            "item": {
                "question": question,
                "answer": ""
            },
            "planning_port": planning_port
        }

        try:
            # 运行研究
            result = agent._run(input_data, model_path)

            # 显示结果
            if "prediction" in result:
                print(f"答案: {result['prediction'][:200]}...")  # 显示前200个字符

            if "termination" in result:
                print(f"终止状态: {result['termination']}")

            # 显示对话轮数
            if "messages" in result:
                rounds = len([msg for msg in result["messages"] if msg["role"] == "assistant"])
                print(f"对话轮数: {rounds}")

        except Exception as e:
            print(f"错误: {e}")

        print("\n" + "="*50)


def batch_research_example():
    """批量研究示例"""
    print("DeepResearch 批量研究示例")
    print("="*50)

    # 配置（同上）
    model_path = "alibaba/tongyi-deepresearch-30b-a3b"  # OpenRouter 模型名称
    planning_port = 6001

    llm_cfg = {
        'model': model_path,
        'generate_cfg': {
            'max_input_tokens': 320000,
            'max_retries': 10,
            'temperature': 0.6,
            'top_p': 0.95,
            'presence_penalty': 1.1
        },
        'model_type': 'openai'  # 使用 OpenAI 兼容的 API
    }

    agent = MultiTurnReactAgent(
        llm=llm_cfg,
        function_list=["search", "visit", "google_scholar", "PythonInterpreter"]
    )

    # 批量问题
    batch_questions = [
        {
            "id": 1,
            "question": "分析人工智能在医疗领域的应用",
            "category": "医疗AI"
        },
        {
            "id": 2,
            "question": "研究区块链技术的最新发展",
            "category": "区块链"
        },
        {
            "id": 3,
            "question": "总结量子计算的进展",
            "category": "量子计算"
        }
    ]

    results = []

    for item in batch_questions:
        print(f"\n处理 [{item['category']}] {item['question']}")
        print("-" * 50)

        input_data = {
            "item": {
                "question": item["question"],
                "answer": ""
            },
            "planning_port": planning_port
        }

        try:
            result = agent._run(input_data, model_path)

            # 保存结果
            results.append({
                "id": item["id"],
                "category": item["category"],
                "question": item["question"],
                "result": result.get("prediction", ""),
                "termination": result.get("termination", ""),
                "success": "prediction" in result
            })

            print(f"状态: {'成功' if result.get('prediction') else '失败'}")

        except Exception as e:
            print(f"错误: {e}")
            results.append({
                "id": item["id"],
                "category": item["category"],
                "question": item["question"],
                "error": str(e),
                "success": False
            })

    # 保存批量结果
    output_file = "examples/batch_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n批量处理完成！结果已保存到 {output_file}")

    # 显示统计
    successful = sum(1 for r in results if r.get("success", False))
    print(f"成功: {successful}/{len(results)}")


def custom_config_example():
    """自定义配置示例"""
    print("DeepResearch 自定义配置示例")
    print("="*50)

    # 自定义配置
    model_path = "alibaba/tongyi-deepresearch-30b-a3b"  # OpenRouter 模型名称
    planning_port = 6001

    # 自定义LLM配置
    llm_cfg = {
        'model': model_path,
        'generate_cfg': {
            'max_input_tokens': 128000,  # 较小的上下文
            'max_retries': 5,           # 较少的重试
            'temperature': 0.3,         # 更低的温度
            'top_p': 0.9,              # 更保守的采样
            'presence_penalty': 0.8     # 较小的存在惩罚
        },
        'model_type': 'openai'  # 使用 OpenAI 兼容的 API
    }

    # 只使用部分工具
    agent = MultiTurnReactAgent(
        llm=llm_cfg,
        function_list=["search", "visit"]  # 只使用搜索和访问
    )

    question = "什么是深度学习？"
    print(f"问题: {question}")
    print("-" * 50)

    input_data = {
        "item": {
            "question": question,
            "answer": ""
        },
        "planning_port": planning_port
    }

    try:
        result = agent._run(input_data, model_path)

        if "prediction" in result:
            print(f"答案: {result['prediction']}")

        # 显示配置信息
        print(f"\n使用的配置:")
        print(f"- 最大输入tokens: {llm_cfg['generate_cfg']['max_input_tokens']}")
        print(f"- 温度: {llm_cfg['generate_cfg']['temperature']}")
        print(f"- 可用工具: {agent.function_list}")

    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    print("选择示例类型:")
    print("1. 简单研究示例")
    print("2. 批量研究示例")
    print("3. 自定义配置示例")

    choice = input("请选择 (1-3): ").strip()

    if choice == "1":
        simple_research_example()
    elif choice == "2":
        batch_research_example()
    elif choice == "3":
        custom_config_example()
    else:
        print("无效选择，运行简单示例")
        simple_research_example()