import asyncio
import functools
from typing import Callable, Any


async def run_in_threadpool(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    loop = asyncio.get_running_loop()
    pfunc = functools.partial(func, *args, **kwargs)
    return await loop.run_in_executor(None, pfunc)