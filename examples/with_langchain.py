import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch


llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    model="alibaba/tongyi-deepresearch-30b-a3b",  # 模型指向 Tongyi DeepResearch
    temperature=0,
    timeout=120,
)

# ① 搜索工具（也可换 Serper/SearxNG/Exa 等）
search = TavilySearch(max_results=3)  # 需要 TAVILY_API_KEY
tools = [search]

# ② 一行创建 ReAct 代理（单一 llm agent + search_tools）
agent = create_react_agent(model=llm, tools=tools, prompt="你是可靠的深度检索助手。")

# ③ 调用
out = agent.invoke({"messages": [{"role": "user", "content": "检索并汇总近一周GraphRAG的新资料，给出处。"}]})
print(out["messages"][-1].content)
