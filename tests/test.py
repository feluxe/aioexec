from time import time
from typing import NamedTuple
from itertools import repeat, chain
from aioexec import Threads, Procs, Call
import asyncio as aio


class Conf(NamedTuple):
    workers: int
    num_to_find: str
    limit: int
    ratio: int
    chunk_amount: int


def findmatches(start, end, num):
    matches = []

    for n in range(start, end):
        if num in str(n):
            matches.append(n)

    return matches


async def run(s: Conf):

    chunk_len = s.limit // s.chunk_amount

    chunks = (
        (cstart * chunk_len, cstart * chunk_len + chunk_len)
        for cstart in range(0, s.chunk_amount)
    )

    results = await aio.gather(
        *Procs(s.workers).batch(
            Call(findmatches, chunk[0], chunk[1], s.num_to_find)
            for chunk in chunks
        )
    )

    return list(chain.from_iterable(results))


if __name__ == '__main__':

    s = Conf(
        workers=6,
        num_to_find=str(5),
        limit=int(1E8),
        ratio=30,
        chunk_amount=int(30 * 6),
    )

    start = time()

    loop = aio.get_event_loop()
    matches = loop.run_until_complete(run(s))

    end = time() - start

    print(f'limit={s.limit}, workers={s.workers}')
    print(f"found {len(matches)} in {end} sec")
