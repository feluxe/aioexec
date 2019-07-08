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
                return self.loop.run_in_executor(
                    pool, partial(fn, *args, **kwargs)
                )
        else:
            return self.loop.run_in_executor(
                self.pool, partial(fn, *args, **kwargs)
            )

    def batch(
        self,
        *calls: Union[Call, Iterator[Call]],
    ) -> Iterator[Awaitable[Any]]:

        if not self.loop:
            self.loop = asyncio.get_event_loop()

        if not self.pool:

            with self.Executor(self.n) as pool:

                for c in calls:
                    if isinstance(c, GeneratorType):
                        for x in c:
                            yield self.loop.run_in_executor(
                                pool, partial(x.fn, *x.args, **x.kwargs)
                            )
                    elif isinstance(c, list):
                        yield self.loop.run_in_executor(
                            pool, partial(c.fn, *c.args, **c.kwargs)
                        )
        else:
            for c in calls:
                if isinstance(c, GeneratorType):
                    for x in c:
                        yield self.loop.run_in_executor(
                            self.pool, partial(x.fn, *x.args, **x.kwargs)
                        )
                elif isinstance(c, list):
                    yield self.loop.run_in_executor(
                        self.pool, partial(c.fn, *c.args, **c.kwargs)
                    )


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


class Coros():
    pass
