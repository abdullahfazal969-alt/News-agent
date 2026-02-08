import asyncio
import time
from typing import Any, Dict, List, Type

from src.agent.base_agent import BaseAgent, ReportType
from src.agent.strategies import ResearchStrategy, SummarizeCategorizeStrategy
from src.config.models import (
    AgentConfig,
    ArticleAnalysisResult,
    NewsAgentReport,
    RawArticleData,
)
from src.tools.mock_news_api import async_mock_fetch_article_content
from src.utils.executor_manager import (
    ExecutorManager,
)  # ProcessPoolExecutor is managed here


class NewsArticleAgent(BaseAgent[NewsAgentReport]):
    """
    An AI agent that fetches news articles, summarizes and categorizes them
    using a hybrid I/O-bound (asyncio) and CPU-bound (ProcessPoolExecutor) workload pattern.
    """

    def __init__(
        self,
        agent_config: AgentConfig,
        executor_manager: ExecutorManager,
        strategy_type: Type[ResearchStrategy] = SummarizeCategorizeStrategy,
    ):
        self.agent_config = agent_config
        self.executor_manager = executor_manager
        # Initialize the chosen strategy
        self.strategy: ResearchStrategy = strategy_type(agent_config=self.agent_config)

    async def research(self, urls: List[str]) -> NewsAgentReport:
        """
        Orchestrates the fetching and processing of multiple news articles
        using the hybrid workload pattern.
        """
        start_time = time.perf_counter()
        print(f"--- Agent: Starting research for {len(urls)} articles ---")

        # Step 1: Concurrently fetch all articles (I/O-bound)
        # We launch all fetch tasks simultaneously using asyncio.gather
        fetch_tasks = [
            async_mock_fetch_article_content(url, self.agent_config.mock_fetch_delay)
            for url in urls
        ]
        # Wait for all fetches to complete. The event loop remains responsive during this.
        all_raw_articles: List[RawArticleData] = await asyncio.gather(*fetch_tasks)

        # Step 2: Concurrently hand off CPU-bound processing for each article to the executor
        # As soon as an article is fetched, we pass it for processing.
        # These will run in parallel on separate CPU cores via ProcessPoolExecutor.
        process_tasks = [
            self.strategy.process_article(raw_article, self.executor_manager.executor)
            for raw_article in all_raw_articles
        ]
        # Wait for all processing tasks (running in the executor) to complete.
        all_analysis_results: List[ArticleAnalysisResult] = await asyncio.gather(
            *process_tasks
        )

        end_time = time.perf_counter()
        total_duration = end_time - start_time

        print(f"--- Agent: Finished research in {total_duration:.2f} seconds ---")

        return NewsAgentReport(
            results=all_analysis_results,
            total_articles_processed=len(urls),
            total_time_taken=total_duration,
            total_duration=total_duration,
        )

        print(f"--- Agent: Finished research in {total_duration:.2f} seconds ---")

        return NewsAgentReport(
            results=all_analysis_results,
            total_articles_processed=len(urls),
            total_time_taken=total_duration,
        )

    async def shutdown(self) -> None:
        """
        The ExecutorManager handles its own shutdown via its aexit method,
        so the agent's shutdown just ensures no other resources are left open.
        """
        print("Agent: Shutting down.")
        # No additional shutdown logic needed here, as executor_manager handles its pool.
        pass
