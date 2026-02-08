import asyncio
import time
import os
from typing import List

from src.config.models import AgentConfig, NewsAgentReport, RawArticleData, ArticleAnalysisResult
from src.utils.executor_manager import ExecutorManager
from src.agent.news_agent import NewsArticleAgent
from src.tools.mock_news_api import async_mock_fetch_article_content, cpu_mock_analyze_article_text # For sequential comparison

async def main() -> None:
    """
    Main entry point for the News Article Agent application.
    Orchestrates the agent's workflow, demonstrating hybrid I/O and CPU processing.
    """
    print("--- Starting News Article Agent Application ---")

    # 1. Load Agent Configuration
    # AgentConfig automatically loads from .env or uses defaults
    agent_config = AgentConfig()
    print(f"Agent Config Loaded: max_cpu_workers={agent_config.max_cpu_workers}, "
          f"mock_fetch_delay={agent_config.mock_fetch_delay:.2f}s, "
          f"mock_analysis_time={agent_config.mock_analysis_time:.2f}s")

    # 2. Define Mock Article URLs for demonstration
    # This list will trigger the hybrid workload pattern
    mock_article_urls = [
        "http://example.com/ai_breakthrough_1",
        "http://example.com/quantum_computing_2",
        "http://example.com/robotics_advances_3",
        "http://example.com/mlops_best_practices_4",
        "http://example.com/data_privacy_concerns_5",
        "http://example.com/ethical_ai_guidelines_6"
    ]

    # 3. Initialize ExecutorManager and NewsArticleAgent within an async context
    # The ExecutorManager handles the ProcessPoolExecutor lifecycle
    async with ExecutorManager(max_workers=agent_config.max_cpu_workers) as executor_manager:
        agent = NewsArticleAgent(
            agent_config=agent_config,
            executor_manager=executor_manager
        )

        # 4. Run the Agent's research method
        try:
            report: NewsAgentReport = await agent.research(mock_article_urls)

            # 5. Print the final report
            print("\n--- Final Agent Research Report ---")
            print(f"Total articles processed: {report.total_articles_processed}")
            print(f"Total time taken (Hybrid Pattern): {report.total_time_taken:.2f} seconds")
            for result in report.results:
                print(f"  URL: {result.url}")
                print(f"    Category: {result.category}")
                print(f"    Summary: {result.summary[:70]}...") # Print first 70 chars of summary
                print(f"    Entities: {', '.join(result.entities)}")
                print("-" * 20)

            # Optional: Simulate a sequential run to highlight performance gain
            print("\n--- Simulating Sequential Run for Comparison ---")
            sequential_start_time = time.perf_counter()
            sequential_results: List[ArticleAnalysisResult] = []
            print("Note: This is a simplified sequential simulation within one process.")
            for url in mock_article_urls:
                raw_data = await async_mock_fetch_article_content(url, agent_config.mock_fetch_delay)
                analysis_result = cpu_mock_analyze_article_text(raw_data, agent_config.mock_analysis_time)
                sequential_results.append(analysis_result)
            sequential_end_time = time.perf_counter()
            sequential_duration = sequential_end_time - sequential_start_time
            
            print(f"Sequential processing for {len(mock_article_urls)} articles: {sequential_duration:.2f} seconds")
            print(f"Hybrid pattern achieved a speedup of: {sequential_duration / report.total_time_taken:.2f}x")

        except Exception as e:
            print(f"An error occurred during agent execution: {e}")

    print("--- News Article Agent Application Finished ---")

if __name__ == "__main__":
    # Ensure src is in PYTHONPATH for local imports to work, though uv usually sets this up.
    asyncio.run(main())