from refactor.tongyi_ds.config import GraphBuildConfig

from refactor.tongyi_ds.graph import run_tongyi_deepresearch

def run_research(question: str):
    config = GraphBuildConfig(
        tool_names=["search", "visit", "google_scholar"],
    )
    result = run_tongyi_deepresearch(question, config=config)
    return result


if __name__ == "__main__":
    result = run_research("A Survey on RAG")
    print(result)