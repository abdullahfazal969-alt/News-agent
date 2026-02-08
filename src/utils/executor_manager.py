import asyncio
from concurrent.futures import ProcessPoolExecutor # Using ProcessPoolExecutor for standard compatibility
from typing import Callable, Any, List, Optional

class ExecutorManager:
    """
    Manages the lifecycle of a ProcessPoolExecutor for offloading CPU-bound tasks.
    """
    def __init__(self, max_workers: int):
        self._max_workers = max_workers
        self._executor: Optional[ProcessPoolExecutor] = None

    async def __aenter__(self) -> 'ExecutorManager':
        """Initializes the ProcessPoolExecutor when entering the async context."""
        print(f"Initializing ProcessPoolExecutor with {self._max_workers} workers...")
        self._executor = ProcessPoolExecutor(max_workers=self._max_workers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Shuts down the ProcessPoolExecutor when exiting the async context."""
        if self._executor:
            print("Shutting down ProcessPoolExecutor...")
            self._executor.shutdown(wait=True)
            self._executor = None
        print("ProcessPoolExecutor shut down.")

    @property
    def executor(self) -> ProcessPoolExecutor:
        """Provides access to the initialized executor."""
        if not self._executor:
            raise RuntimeError("Executor not initialized. Use ExecutorManager as an async context manager.")
        return self._executor

async def run_cpu_task_in_executor(
    executor: ProcessPoolExecutor,
    func: Callable[..., Any],
    *args: Any,
    **kwargs: Any
) -> Any:
    """
    Runs a synchronous, CPU-bound function in the provided executor,
    without blocking the asyncio event loop.
    """
    loop = asyncio.get_running_loop()
    # run_in_executor is the bridge! It tells the event loop to hand off
    # this blocking call to a worker in the ProcessPoolExecutor.
    # While the worker runs the CPU-bound 'func', the event loop is free
    # to continue processing other async (I/O-bound) tasks.
    return await loop.run_in_executor(executor, func, *args, **kwargs)

