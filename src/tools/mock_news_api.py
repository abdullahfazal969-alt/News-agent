import asyncio
import time
import random
from typing import Dict, Any
from src.config.models import RawArticleData, ArticleAnalysisResult

async def async_mock_fetch_article_content(
    url: str,
    mock_fetch_delay: float
) -> RawArticleData:
    """
    Simulates fetching an article's content from a URL with network latency.
    Returns structured raw article data.
    """
    start_time = time.perf_counter()
    print(f"[I/O Mock]: Fetching content for {url} (simulated delay: {mock_fetch_delay:.2f}s)")
    await asyncio.sleep(mock_fetch_delay) # Simulate network latency

    # Generate some mock content
    mock_content = (
        f"This is the mock content for the article at {url}. "
        f"It discusses a breakthrough in AI engineering, using asyncio and hybrid workloads. "
        f"Key entities include Gemini, Pydantic, and ProcessPoolExecutor. "
        f"The article also touches on multi-agent systems and real-world applications."
    )
    end_time = time.perf_counter()
    fetch_duration = end_time - start_time

    return RawArticleData(
        url=url,
        content=mock_content,
        fetch_time=fetch_duration
    )

def cpu_mock_analyze_article_text(
    raw_article_data: RawArticleData,
    mock_analysis_time: float
) -> ArticleAnalysisResult:
    """
    Simulates CPU-intensive analysis of article text (summarization, categorization, entity extraction).
    This is a synchronous, blocking function.
    """
    start_time = time.perf_counter()
    print(f"  [CPU Mock]: Analyzing content for {raw_article_data.url} (simulated time: {mock_analysis_time:.2f}s)")
    
    # Simulate heavy CPU processing
    time.sleep(mock_analysis_time)

    # Generate mock analysis results based on the content or URL
    summary = f"Summary of {raw_article_data.url}: AI engineering concepts applied to multi-agent systems."
    category = "Technology" if "AI engineering" in raw_article_data.content else "General"
    entities = ["Gemini", "Pydantic", "ProcessPoolExecutor", "asyncio"]

    end_time = time.perf_counter()
    analysis_duration = end_time - start_time

    return ArticleAnalysisResult(
        url=raw_article_data.url,
        summary=summary,
        category=category,
        entities=entities,
        analysis_time=analysis_duration
    )

