"""
DeepResearch 简单使用示例
展示基本的DeepResearch调用方式
"""
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



if __name__ == "__main__":
    simple_research_example()