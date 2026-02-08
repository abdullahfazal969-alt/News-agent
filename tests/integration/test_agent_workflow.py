import pytest
import asyncio
import time
from typing import List

from src.config.models import AgentConfig, NewsAgentReport, RawArticleData, ArticleAnalysisResult
from src.utils.executor_manager import ExecutorManager, run_cpu_task_in_executor
from src.tools.mock_news_api import async_mock_fetch_article_content, cpu_mock_analyze_article_text
from src.agent.news_agent import NewsArticleAgent
from src.agent.strategies import SummarizeCategorizeStrategy


# --- Fixtures for Agent Configuration ---
@pytest.fixture
def agent_config() -> AgentConfig:
    """Provides a default AgentConfig instance for tests."""
    return AgentConfig(
        max_cpu_workers=2,
        mock_fetch_delay=0.1,  # Shorter delays for faster tests
        mock_analysis_time=0.2, # Shorter times for faster tests
        api_timeout=5.0
    )

@pytest.fixture
async def executor_manager(agent_config: AgentConfig):
    """Provides an initialized ExecutorManager as an async context manager."""
    async with ExecutorManager(max_workers=agent_config.max_cpu_workers) as manager:
        yield manager

@pytest.fixture
async def news_agent(agent_config: AgentConfig, executor_manager: ExecutorManager) -> NewsArticleAgent:
    """Provides an initialized NewsArticleAgent instance."""
    agent = NewsArticleAgent(
        agent_config=agent_config,
        executor_manager=executor_manager,
        strategy_type=SummarizeCategorizeStrategy
    )
    yield agent
    await agent.shutdown() # Ensure agent shutdown is called

# --- Test Cases ---
@pytest.mark.asyncio
async def test_agent_workflow_single_article(news_agent: NewsArticleAgent, agent_config: AgentConfig):
    """
    Tests the agent's workflow with a single article.
    Checks if results are correct and time is within expected range.
    """
    urls = ["http://mock.test/article1"]
    
    start_time = time.perf_counter()
    report = await news_agent.research(urls)
    end_time = time.perf_counter()

    assert report.total_articles_processed == 1
    assert len(report.results) == 1
    assert report.results[0].url == urls[0]
    assert "Summary of" in report.results[0].summary
    assert "Technology" in report.results[0].category
    
    # Expected time: 1x fetch delay + 1x analysis time = 0.1s + 0.2s = 0.3s
    # Allow for some minor overhead, but it should be close.
    expected_min_time = agent_config.mock_fetch_delay + agent_config.mock_analysis_time
    assert report.total_time_taken >= expected_min_time * 0.9 # Allow 10% below for precision
    assert report.total_time_taken <= expected_min_time * 1.5 # Allow 50% above for overhead


@pytest.mark.asyncio
async def test_agent_workflow_multiple_articles_hybrid_performance(news_agent: NewsArticleAgent, agent_config: AgentConfig):
    """
    Tests the agent's workflow with multiple articles, focusing on hybrid performance.
    Demonstrates overlapping I/O and CPU work.
    """
    urls = [f"http://mock.test/article{i}" for i in range(1, 5)] # 4 articles
    
    start_time = time.perf_counter()
    report = await news_agent.research(urls)
    end_time = time.perf_counter()

    assert report.total_articles_processed == len(urls)
    assert len(report.results) == len(urls)
    
    # --- Performance Assertion for Hybrid Workload ---
    # Expected time for 4 articles (0.1s fetch, 0.2s analysis) with 2 CPU workers:
    # T=0:  I/O F1, F2 (concurrent)
    # T=0.1:F1 finishes. CPU P1 starts. F3 starts. F2 continues.
    # T=0.2:F2 finishes. CPU P2 starts. F4 starts. P1 continues.
    # T=0.3:F3 finishes. P1, P2 continue.
    # T=0.4:F4 finishes. P1, P2 continue.
    # T=0.3 (P1 finishes) or T=0.4 (P2 finishes)
    # Total effective CPU time for 4 items with 2 workers = (4 items / 2 workers) * 0.2s_per_item = 2 * 0.2s = 0.4s
    # So, roughly: (first fetch delay) + (total effective CPU time)
    # = 0.1s + 0.4s = 0.5s (this is a very simplified ideal scenario)
    # In practice, it's:
    # Max(fetch_delay) + (num_articles / max_cpu_workers) * analysis_time
    # = 0.1 + (ceil(4/2) * 0.2) = 0.1 + 0.4 = 0.5s
    # Add initial fetch time for the first batch, and then the parallel CPU time.
    
    # Simplified expectation for total time:
    # (mock_fetch_delay) + (ceil(num_articles / max_cpu_workers) * mock_analysis_time)
    # 0.1 + (ceil(4/2) * 0.2) = 0.1 + (2 * 0.2) = 0.1 + 0.4 = 0.5 seconds
    
    expected_hybrid_time = agent_config.mock_fetch_delay + (len(urls) / agent_config.max_cpu_workers) * agent_config.mock_analysis_time
    
    # Test should be significantly faster than sequential:
    sequential_time = len(urls) * (agent_config.mock_fetch_delay + agent_config.mock_analysis_time) # 4 * (0.1 + 0.2) = 1.2s
    
    print(f"
Sequential time: {sequential_time:.2f}s, Expected Hybrid time: {expected_hybrid_time:.2f}s, Actual: {report.total_time_taken:.2f}s")

    assert report.total_time_taken < sequential_time * 0.7 # Should be at least 30% faster than sequential
    assert report.total_time_taken <= expected_hybrid_time * 1.5 # Allow for some overhead
    assert report.total_time_taken >= expected_hybrid_time * 0.7 # Ensure it's not too fast either (indicating not enough work)
