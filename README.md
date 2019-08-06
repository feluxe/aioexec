# aioexec

## Description

Aioexec is a simple, intuitive interface around the `concurrent.futures` package and asyncio's `loop.run_in_executor` method. Aioexec is leightweight, no dependencies and ~100 LOC.

## Requirements

aioexec requires Python `>= 3.7`

## Install

    pip install aioexec

or

    pipenv install aioexec

## Usage

**Without** `aioexec` you usually run an executor something like this:

```python
import aysncio
from concurrent.futures import ProcessPoolExecutor

# ...

loop = asyncio.get_event_loop()

foo = await loop.run_in_executor(
    ProcessPoolExecutor(1), lambda: my_func(foo='baz')
)
```

**With** `aioexec` you would do the same like this:

```python
from aioexec import Procs

# ...

foo = await Procs(1).call(my_func, foo='baz')
```

You can call a `batch` of functions in the same executor like this:

```python
import asyncio
from aioexec import Procs, Call

# ...

my_values = await asyncio.gather(
    *Procs(3).batch(
        Call(my_func, foo='bar'),
        Call(my_func, foo='baz'),
        Call(my_func, foo='qux'),
    )
)
```

This plays nicely with comprehensions:

```python
my_values = await asyncio.gather(
    *Procs(10).batch(
        Call(my_func, foo=i) for i in range(0, 10)
    )
)
```

You can also spawn a `pool` in a context and make multiple different calls with the same executor:

```python
with Procs(10) as pool:

    value_a = await pool.call(my_func, foo='baz')

    value_b = await aio.gather(
        *pool.batch(
            Call(my_func, foo=i) for i in range(0, 10)
        )
    )

    # etc...
```

The examples from above work the same for `Threads`, e.g.:

```python
from aioexec import Threads

# ...

foo = await Threads(1).call(my_func, foo='baz')

```

If necessary, you can pass an event `loop` to the executors like this:

```python
foo = await Threads(1, my_loop).call(my_func, foo='baz')
foo = await Procs(1, my_loop).call(my_func, foo='baz')
```

You can also pass async functions to an executor:

```python
async def my_async_func(foo):
    return await stuff(foo)


foo = await Procs(1, my_loop).call(my_async_func, foo='baz')
```

## Development / Testing

Clone the repo and install dev packages:

    pipenv install --dev

Run tests:

    pipenv run python make.py test
