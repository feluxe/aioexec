"""
"""
from functools import partial
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Optional, Pattern, List, NamedTuple, Callable, Awaitable, Iterable, Generator
from types import GeneratorType
import asyncio


class Call:

    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


def _call(executor, loop, fn, *args, **kwargs):

    if not loop:
        loop = asyncio.get_event_loop()

    return loop.run_in_executor(executor, partial(fn, *args, **kwargs))


def _batch(executor, loop, *calls):

    if not loop:
        loop = asyncio.get_event_loop()

    for c in calls:
        if type(c) == GeneratorType:
            for x in c:
                yield loop.run_in_executor(
                    executor, partial(x.fn, *x.args, **x.kwargs)
                )
        else:
            yield loop.run_in_executor(
                executor, partial(c.fn, *c.args, **c.kwargs)
            )


class Concurrent:

    def __init__(
        self,
        Executor=None,
        n=None,
        loop=None,
    ):
        self.Executor = Executor
        self.n = n
        self.loop = loop
        self.executor = None
        self.call = partial(_call, self.Executor(self.n), self.loop)
        self.batch = partial(_batch, self.Executor(self.n), self.loop)


class Threads(Concurrent):

    def __init__(self, n=None, loop=None):
        Concurrent.__init__(self, ThreadPoolExecutor, n, loop)


class Procs(Concurrent):

    def __init__(self, n=None, loop=None):
        Concurrent.__init__(self, ProcessPoolExecutor, n, loop)


class Coros():
    pass

