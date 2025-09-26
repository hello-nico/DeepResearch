import asyncio

import pytest

from refactor.tongyi_ds.tools.tool_visit import Visit


@pytest.mark.asyncio
async def test_visit_prefers_jina(monkeypatch):
    visit = Visit()

    monkeypatch.setattr(Visit, "_fetch_via_jina", lambda self, url: "# Title\ncontent")

    async def fake_crawl(self, url, pdf):
        raise AssertionError("Crawl4AI should not be called when Jina succeeds")

    monkeypatch.setattr(Visit, "_fetch_with_crawl4ai", fake_crawl)
    monkeypatch.setattr(
        Visit,
        "_summarize_content",
        lambda self, content, goal, summarizer, max_retries: {
            "summary": "summary text",
            "evidence": "evidence text",
        },
    )

    result = await visit._read_and_summarize("https://example.com", "test goal")
    assert "summary text" in result
    assert "evidence text" in result


@pytest.mark.asyncio
async def test_visit_falls_back_to_crawl4ai(monkeypatch):
    visit = Visit()

    monkeypatch.setattr(Visit, "_fetch_via_jina", lambda self, url: "")

    async def fake_crawl(self, url, pdf):
        return "fallback markdown", {"source": "crawl4ai"}

    monkeypatch.setattr(Visit, "_fetch_with_crawl4ai", fake_crawl)
    monkeypatch.setattr(
        Visit,
        "_summarize_content",
        lambda self, content, goal, summarizer, max_retries: {
            "summary": "crawl summary",
            "evidence": "crawl evidence",
        },
    )

    result = await visit._read_and_summarize("https://example.com/fallback", "goal")
    assert "crawl summary" in result
    assert "crawl evidence" in result


def test_visit_call_batches_multiple_urls(monkeypatch):
    visit = Visit()

    async def fake_read(url, goal):
        await asyncio.sleep(0)
        return f"content-for-{url}-{goal}"

    monkeypatch.setattr(Visit, "_read_and_summarize", fake_read)

    output = visit.call({"url": ["https://a", "https://b"], "goal": "goal"})
    assert "content-for-https://a-goal" in output
    assert "content-for-https://b-goal" in output
    assert "===" in output
