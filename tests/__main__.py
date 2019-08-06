from time import time, sleep
import random
from typing import NamedTuple, Awaitable, Tuple, Union, Type, Iterator, List
from itertools import repeat, chain
import asyncio as aio
from aioexec import Threads, Procs, Call

ExecutorType = Union[Type[Procs], Type[Threads]]


class Conf(NamedTuple):
    workers: int
    num_to_find: str
    limit: int
    chunk_size: int


def get_values_sync():
    t = random.uniform(0.0001, 0.001)
    sleep(t)
    return [1, 2, 3]


async def get_values_async():
    t = random.uniform(0.0001, 0.001)
    await aio.sleep(t)
    return [1, 2, 3]


async def test_call_async(Executor, c):
    print("Test call() async")

    start = time()
    workers = 1

    results = await aio.gather(
        Executor(workers).call(get_values_async),
        Executor(workers).call(get_values_async),
        Executor(workers).call(get_values_sync),
        Executor(workers).call(get_values_async),
    )

    results = await aio.gather(
        *Executor(workers).batch(
            Call(get_values_async),
            Call(get_values_async),
            Call(get_values_sync),
            Call(get_values_async),
        )
    )
    print('Test Done')
    print(results)

    t_delta = time() - start

    return len(list(chain.from_iterable(results))), t_delta


async def test_call_args(
    Executor: ExecutorType,
    c: Conf,
) -> Tuple[int, float]:

    print("Test call() with *args")

    start = time()

    results = await aio.gather(
        *[Executor(c.workers).call(get_values_sync) for i in range(100)]
    )

    t_delta = time() - start

    return len(list(chain.from_iterable(results))), t_delta


async def test_call_args_list(
    Executor: ExecutorType,
    c: Conf,
) -> Tuple[int, float]:

    print("Test call() with list as arg")

    start = time()

    results = await aio.gather(
        [Executor(c.workers).call(get_values_sync) for i in range(100)]
    )

    t_delta = time() - start

    return len(list(chain.from_iterable(results))), t_delta


async def test_call_args_generator(
    Executor: ExecutorType,
    c: Conf,
) -> Tuple[int, float]:

    print("Test call() with generator as arg")

    start = time()

    results = await aio.gather(
        *(Executor(c.workers).call(get_values_sync) for i in range(100))
    )

    t_delta = time() - start

    return len(list(chain.from_iterable(results))), t_delta


async def test_batch(
    Executor: ExecutorType,
    c: Conf,
) -> Tuple[int, float]:

    print("Test Batch")

    start = time()

    n = c.workers

    results = await aio.gather(
        *Executor(n).batch(Call(get_values_sync) for i in range(100))
    )

    t_delta = time() - start

    return len(list(chain.from_iterable(results))), t_delta


async def test_pool_call(
    Executor: ExecutorType,
    c: Conf,
) -> Tuple[int, float]:

    print("Test Pool Call")

    start = time()

    n = c.workers

    with Executor(n) as pool:

        results = await aio.gather(
            *(pool.call(get_values_sync) for i in range(100))
        )

    t_delta = time() - start

    return len(list(chain.from_iterable(results))), t_delta


async def test_pool_batch(
    Executor: ExecutorType,
    c: Conf,
) -> Tuple[int, float]:

    print("Test Pool Batch")

    start = time()

    n = c.workers

    with Executor(n) as pool:

        results = await aio.gather(
            *pool.batch(
                *[Call(get_values_sync) for i in range(100)],
            )
        )

    t_delta = time() - start

    return len(list(chain.from_iterable(results))), t_delta


def run() -> None:

    conf = Conf(
        workers=8,
        num_to_find="5",
        chunk_size=200,
        limit=10000,
    )

    print(f'Run Tests: limit={conf.limit}, workers={conf.workers}')

    loop = aio.get_event_loop()

    results = [
        loop.run_until_complete(test_call_async(Procs, conf)),
        loop.run_until_complete(test_call_args(Procs, conf)),
        # loop.run_until_complete(test_call_args_list(Procs, conf)),
        loop.run_until_complete(test_call_args_generator(Procs, conf)),
        loop.run_until_complete(test_batch(Procs, conf)),
        loop.run_until_complete(test_pool_call(Procs, conf)),
        loop.run_until_complete(test_pool_batch(Procs, conf)),
    ]

    print("Proc Test Results:")

    for result in results:
        print(f"found {result[0]} in {result[1]} sec")

    results = [
        loop.run_until_complete(test_call_args(Threads, conf)),
        # loop.run_until_complete(test_call_args_list(Threads, conf)),
        loop.run_until_complete(test_call_args_generator(Threads, conf)),
        loop.run_until_complete(test_batch(Threads, conf)),
        loop.run_until_complete(test_pool_call(Threads, conf)),
        loop.run_until_complete(test_pool_batch(Threads, conf)),
    ]

    print("Thread Test Results:")

    for result in results:
        print(f"found {result[0]} in {result[1]} sec")


if __name__ == '__main__':
    run()
