from react_agent import MultiTurnReactAgent


def research_demo():

    # 配置模型
    model_path = "alibaba/tongyi-deepresearch-30b-a3b"

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
        function_list=["search", "visit", "google_scholar"]
    )

    # 问题
    questions = [
        "A Survey on RAG"
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
            "planning_port": 6000
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
                
            print(result)

        except Exception as e:
            print(f"错误: {e}")

        print("\n" + "="*50)



if __name__ == "__main__":
    research_demo()