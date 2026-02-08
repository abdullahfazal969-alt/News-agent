from abc import ABC, abstractmethod
from typing import List
from src.config.models import RawArticleData, ArticleAnalysisResult, AgentConfig
from src.tools.mock_news_api import cpu_mock_analyze_article_text
from src.utils.executor_manager import run_cpu_task_in_executor
from concurrent.futures import ProcessPoolExecutor # or InterpreterPoolExecutor

class ResearchStrategy(ABC):
    """
    Abstract base class for research strategies.
    Defines the interface for how an article should be processed (CPU-bound).
    """
    def __init__(self, agent_config: AgentConfig):
        self.agent_config = agent_config

    @abstractmethod
    async def process_article(self,
                              raw_article_data: RawArticleData,
                              executor: ProcessPoolExecutor # or InterpreterPoolExecutor
                             ) -> ArticleAnalysisResult:
        """
        Processes a single raw article to produce an analysis result.
        This method should orchestrate CPU-bound tasks in the executor.
        """
        pass

class SummarizeCategorizeStrategy(ResearchStrategy):
    """
    A concrete research strategy that summarizes and categorizes an article
    using a CPU-bound mock analysis tool.
    """
    async def process_article(self,
                              raw_article_data: RawArticleData,
                              executor: ProcessPoolExecutor # or InterpreterPoolExecutor
                             ) -> ArticleAnalysisResult:
        """
        Uses the CPU mock tool to analyze the article, returning a summary and category.
        """
        return await run_cpu_task_in_executor(
            executor,
            cpu_mock_analyze_article_text,
            raw_article_data,
            self.agent_config.mock_analysis_time
        )

