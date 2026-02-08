# 📰 News Article Summarizer & Categorizer Agent
    
# Project Overview
    
     This project implements a high-performance AI agent capable of fetching news articles, summarizing their content, and
      categorizing them. It showcases a **Hybrid Workload Pattern** that efficiently combines **concurrent I/O-bound tasks** (simulat
      network calls) with **parallel CPU-bound tasks** (simulated article analysis) to maximize resource utilization and significantl
      reduce overall processing time.
    
     The agent is designed with modularity, type safety, and testability in mind, utilizing modern Python features and best practice
      for AI engineering.
      
# ✨ Key Features
    
  - **Hybrid Workload Pattern:** Demonstrates the efficient overlap of asynchronous I/O with multiprocessing for CPU-bound tasks
  -   **Concurrent I/O:** Utilizes `asyncio` for non-blocking simulation of fetching multiple articles simultaneously.
  -   **Parallel CPU Processing:** Employs `ProcessPoolExecutor` (or `InterpreterPoolExecutor` concept) to run CPU-intensive
      summarization and categorization tasks across multiple CPU cores in parallel.
  -   **Type Safety & Data Validation:** Leverages `Pydantic` for strict data modeling and validation of configuration settings,
      raw fetched data, and processed results.
  -   **Modular Design:** Separates concerns into distinct modules for configuration, mock tools, executor management, agent core
      and research strategies.
  -   **Configurable with `.env`:** Easy customization of agent behavior (e.g., number of CPU workers, simulated latencies) via
      environment variables.
  -   **Performance Comparison:** Includes a built-in comparison to sequential processing to highlight speedup.
   
# 🚀 Getting Started
   
  # Prerequisites
   
    -   Python 3.9+
    -   `uv` (recommended package installer and virtual environment manager)
   
  # Installation
   
    **Clone the repository:**
      git clone git@github.com:abdullahfazal969-alt/News-agent.git
      cd News-agent
     **Create and activate a virtual environment with `uv`:**
      uv venv
      source .venv/bin/activate  # On Linux/macOS
  .venv\Scripts\activate   # On Windows (CMD)
  .venv\Scripts\Activate.ps1 # On Windows (PowerShell)


     **Install dependencies:**
      uv add pydantic pydantic-settings pytest
   
  # Configuration
   
    Create a `.env` file in the root of the project to customize agent settings (optional; defaults are provided in
     `src/config/models.py`):
  .env file for News Agent Capstone Project
  MAX_CPU_WORKERS=4           # Number of parallel CPU workers (try matching your CPU cores)
  MOCK_FETCH_DELAY=0.3        # Simulated network latency per article fetch (seconds)
  MOCK_ANALYSIS_TIME=1.0      # Simulated CPU processing time per article (seconds)
  API_TIMEOUT=30.0            # Timeout for external API calls
   
  # 🏃 Usage
   
  # Run the Agent
   
    To run the agent and see the hybrid workload in action:
  uv run src/main.py
   
    You will see output indicating the fetching and processing stages, along with a final report and a performance comparison agains
     sequential execution.
   
  # Run Tests
   
    To execute the integration tests that verify the agent's functionality and performance:
