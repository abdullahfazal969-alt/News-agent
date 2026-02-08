from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

# Define a TypeVar for the specific report type each agent might produce
ReportType = TypeVar('ReportType')

class BaseAgent(ABC, Generic[ReportType]):
    """
    Abstract base class for an AI Agent.
    Defines the common interface for agents.
    """
    @abstractmethod
    async def research(self, query: str) -> ReportType:
        """
        Performs a research task based on the given query.
        Must be implemented by concrete agent classes.
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """
        Performs any necessary cleanup or shutdown procedures for the agent.
        """
        pass

