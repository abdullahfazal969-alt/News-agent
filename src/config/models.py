from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Agent Configuration ---
class AgentConfig(BaseSettings):
    """
    Configuration settings for the News Article Agent.
    Loads from environment variables or a .env file.
    """
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    max_cpu_workers: int = Field(
        default=2, # Default for demonstration, can be changed via env
        description="Maximum number of CPU-bound worker processes for the ProcessPoolExecutor."
    )
    mock_fetch_delay: float = Field(
        default=0.5, # Default for demonstration, can be changed via env
        description="Simulated network latency for mock API calls (in seconds)."
    )
    mock_analysis_time: float = Field(
        default=1.0, # Default for demonstration, can be changed via env
        description="Simulated CPU processing time for mock analysis tasks (in seconds)."
    )
    api_timeout: float = Field(
        default=30.0, # Default for demonstration, can be changed via env
        description="Timeout for external API calls (mock or real)."
    )

# --- Data Models ---
class RawArticleData(BaseModel):
    """Represents raw fetched article content."""
    url: str
    content: str = Field(..., description="The full text content of the article.")
    fetch_time: float = Field(..., description="Time taken to fetch the article (simulated).")

class ArticleAnalysisResult(BaseModel):
    """Represents the results of processing an article."""
    url: str
    summary: str = Field(..., description="A summary of the article content.")
    category: str = Field(..., description="The categorized topic of the article.")
    entities: List[str] = Field(default_factory=list, description="Key entities extracted from the article.")
    analysis_time: float = Field(..., description="Time taken to analyze the article (simulated).")

class NewsAgentReport(BaseModel):
    """Aggregates the results for all processed articles."""
    results: List[ArticleAnalysisResult] = Field(default_factory=list)
    total_articles_processed: int = 0
    total_time_taken: float = 0.0

