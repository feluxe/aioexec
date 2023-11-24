"""
Aioexec is a simple, intuitive interface around the `concurrent.futures` package and
asyncio's `loop.run_in_executor` method. Aioexec is leightweight, no dependencies and
~100 LOC.
"""
from functools import partial
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Optional, List, Callable, Awaitable, Iterable, Any, Union, Iterator
from types import GeneratorType
import asyncio


class Call:
    def __init__(self, fn: Callable, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


def _call_async(fn, args, kwargs):
    new_loop = asyncio.new_event_loop()
    try:
        coro = fn(*args, **kwargs)
        asyncio.set_event_loop(new_loop)
        return new_loop.run_until_complete(coro)
    finally:
        new_loop.close()


def _call(fn, args, kwargs, loop, pool):
    if asyncio.iscoroutinefunction(fn):
        return loop.run_in_executor(pool, partial(_call_async, fn, args, kwargs))
    else:
        return loop.run_in_executor(pool, partial(fn, *args, **kwargs))


def _batch_get_calls(raw_calls):
    for call in raw_calls:
        if isinstance(call, Call):
            yield call

        elif isinstance(call, (GeneratorType, list)):
            for c in call:
                yield c


class ConcurrentBase:
    def __init__(
        self,
        Executor=None,
        n=None,
        loop=None,
    ):
        self.Executor = Executor
        self.n = n
        self.loop = loop
        self.pool = None

    def __enter__(self):
        self.pool = self.Executor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.shutdown(wait=True)
        return False

    def call(self, fn: Callable, *args, **kwargs) -> Awaitable[Any]:
        if not self.loop:
            self.loop = asyncio.get_event_loop()

        if not self.pool:
            with self.Executor(self.n) as pool:
                return _call(fn, args, kwargs, self.loop, pool)
        else:
            return _call(fn, args, kwargs, self.loop, self.pool)

    def batch(
        self,
        *calls: Union[Call, Iterator[Call]],
    ) -> Iterator[Awaitable[Any]]:
        if not self.loop:
            self.loop = asyncio.get_event_loop()

        if not self.pool:
            with self.Executor(self.n) as pool:
                for c in _batch_get_calls(calls):
                    yield _call(c.fn, c.args, c.kwargs, self.loop, pool)

        else:
            for c in _batch_get_calls(calls):
                yield _call(c.fn, c.args, c.kwargs, self.loop, self.pool)


class Threads(ConcurrentBase):
    def __init__(
        self,
        n: Optional[int] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        ConcurrentBase.__init__(self, ThreadPoolExecutor, n, loop)


class Procs(ConcurrentBase):
    def __init__(
        self,
        n: Optional[int] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        ConcurrentBase.__init__(self, ProcessPoolExecutor, n, loop)


class Coros:
    pass
