from time import time
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


def findmatches(start: int, end: int, num_to_find: str) -> List[int]:

    matches = []

    for n in range(start, end):
        if num_to_find in str(n):
            matches.append(n)

    return matches


class Chunk(NamedTuple):
    start: int
    end: int


def get_chunks(c: Conf) -> Iterator[Chunk]:

    chunk_len = c.limit // c.chunk_size

    return (
        Chunk(cstart * chunk_len, cstart * chunk_len + chunk_len)
        for cstart in range(0, c.chunk_size)
    )


async def test_call(
    Executor: ExecutorType,
    c: Conf,
) -> Tuple[int, float]:

    print("Test Call")

    start = time()

    results = await aio.gather(
        *(
            Executor(c.workers).call(
                findmatches,
                chunk.start,
                chunk.end,
                c.num_to_find,
            ) for chunk in get_chunks(c)
        )
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
        *Executor(n).batch(
            Call(findmatches, chunk[0], chunk[1], c.num_to_find)
            for chunk in get_chunks(c)
        )
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
            *(
                pool.call(findmatches, chunk[0], chunk[1], c.num_to_find)
                for chunk in get_chunks(c)
            )
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
                Call(findmatches, chunk[0], chunk[1], c.num_to_find)
                for chunk in get_chunks(c)
            )
        )

    t_delta = time() - start

    return len(list(chain.from_iterable(results))), t_delta


def run() -> None:

    conf = Conf(
        workers=8,
        num_to_find="5",
        chunk_size=200,
        limit=10000000,
    )

    print(f'Run Tests: limit={conf.limit}, workers={conf.workers}')

    loop = aio.get_event_loop()

    results = [
        loop.run_until_complete(test_call(Procs, conf)),
        loop.run_until_complete(test_batch(Procs, conf)),
        loop.run_until_complete(test_pool_call(Procs, conf)),
        loop.run_until_complete(test_pool_batch(Procs, conf)),
    ]

    print("Proc Test Results:")

    for result in results:
        print(f"found {result[0]} in {result[1]} sec")

    results = [
        loop.run_until_complete(test_call(Threads, conf)),
        loop.run_until_complete(test_batch(Threads, conf)),
        loop.run_until_complete(test_pool_call(Threads, conf)),
        loop.run_until_complete(test_pool_batch(Threads, conf)),
    ]

    print("Thread Test Results:")

    for result in results:
        print(f"found {result[0]} in {result[1]} sec")


if __name__ == '__main__':
    run()
