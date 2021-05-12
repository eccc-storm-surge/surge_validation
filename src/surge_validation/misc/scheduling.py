from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

_process_pool_executor = None
_thread_pool_executor = None
DEFAULT_MAX_PROCESS_WORKERS = 20
DEFAULT_MAX_THREAD_WORKERS = 4


def get_process_pool_executor():
    global _process_pool_executor
    if _process_pool_executor is None:
        _process_pool_executor = ProcessPoolExecutor(max_workers=DEFAULT_MAX_PROCESS_WORKERS)
    return _process_pool_executor


def get_thread_pool_executor():
    global _thread_pool_executor
    if _thread_pool_executor is None:
        _thread_pool_executor = ThreadPoolExecutor(max_workers=DEFAULT_MAX_THREAD_WORKERS)
    return _thread_pool_executor
